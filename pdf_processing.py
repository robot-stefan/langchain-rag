from pypdf import PdfReader, PdfWriter 
import pymupdf
from pathlib import Path
from mistralai import Mistral, DocumentURLChunk, ImageURLChunk, TextChunk
from mistralai.models import OCRResponse
from config import configSetting
from configCloud import MISTRALAI_API_KEY, UNSTRUCTURED_API_KEY
from file_operations import filesList, fileMoveToAdded

from langchain_unstructured import UnstructuredLoader
from unstructured.partition.pdf import partition_pdf


import json, os, re, time, backoff, argparse, requests, base64

def main():
    """
    Pdf processing is for splitting up large pdfs for use with cloud OCR tools such as those provided by mistral. 
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_split", action="store_true", 
                        help="Only run pdf splitting operations.")
    parser.add_argument("--ocr_cloud", action="store_true", 
                        help="Only run cloud OCR using mistral.")
    parser.add_argument("--all_ops", action="store_true", 
                        help="Run full collection of operations pdf splitting and cloud OCR.")
    parser.add_argument("--docs_folder", action="store", type=str, default=configSetting.documentPath, 
                        help="Folder where documents are located.")

    args = parser.parse_args()

    if args.pdf_split:
        print("--> Starting PDF Splitting !!!")
        breakdownPdfs(args.docs_folder)
        print("--> PDF Splitting Complete !!!")

    elif args.ocr_cloud:
        print("--> Starting Cloud OCR !!!")
        processMistralPdfOcr(args.docs_folder)
        print("--> Cloud OCR Complete !!!")
    
    elif args.all_ops:
        print("--> Starting Full PDF Processing !!!")
        processPdfs(args.docs_folder)        
        print("--> Full PDF Processing Complete !!!")

def breakdownPdf(file, pageLimit, directory):
    
    with open(file, 'rb') as infile:
        reader = PdfReader(infile)
        page = 0
        writer = PdfWriter()
        total_pages = len(reader.pages)
        # fileNoExt = os.path.splitext(file)[0]
        fileNoExt = os.path.splitext(os.path.basename(file))[0]
        # print(total_pages)
        while page < total_pages:
            writer.add_page(reader.pages[page])
            number = page/pageLimit
            if number.is_integer() == True or page == total_pages-1:
                with open("{}/split/{}-output-{}.pdf".format(directory, fileNoExt, page), 'wb') as outfile:
                    writer.write(outfile)
                    writer = PdfWriter()
            page+=1

def sort_key(s: str) -> list:
    return [int(p)for p in re.findall(r'\D+|\d+', s) if p.isdigit()]

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_response.pages:
        image_data = {}
        # for img in page.images:
            # image_data[img.id] = img.image_base64
        # Replace image placeholders with actual images
        # markdowns.append(replace_images_in_markdown(page.markdown, image_data))
        markdowns.append(page.markdown)

    return "\n\n".join(markdowns)

def get_text_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    for page in ocr_response.pages:
        markdowns.append(page.markdown)

    return "\n\n".join(markdowns)

def mistralImgFromPdfOcr(pdf_file_path):

    client = Mistral(api_key=MISTRALAI_API_KEY)
    fileNoExt = os.path.splitext(pdf_file_path)[0]
    pdf_file = Path(pdf_file_path)

    # Verify PDF file exists
    assert pdf_file.is_file()

    # Open the PDF file
    pdf_document = pymupdf.open(pdf_file)
    text = ""
    json_dict: json = []

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = pix.tobytes(output='jpg', jpg_quality=100)

        # Encode image as base64 for API
        encoded = base64.b64encode(img).decode()
        base64_data_url = f"data:image/jpeg;base64,{encoded}"

        # Perform OCR on the image
        img_response = client.ocr.process(
            document=ImageURLChunk(image_url=base64_data_url),
            model="mistral-ocr-latest",
            retries = 30,
            timeout_ms = 600000,
            )
        
        markdowns: list[str] = []
        pages = img_response.pages
        for page in pages:
            markdowns.append(page.markdown)

        text += img_response.pages[0].markdown
        response_json_dict = json.loads(img_response.model_dump_json())
        json_dict.append(response_json_dict)
        time.sleep(60)
        
    response_json_object = json.dumps(response_json_dict, indent=4)
    with open("{}.json".format(fileNoExt), 'w') as outfile:
        json.dump(response_json_object, outfile)

    markdown_text = text

    # Convert Response to markdown
    with open("{}.md".format(fileNoExt), 'w') as outfile:
        outfile.write(markdown_text)

def mistralPdfOcr(pdf_file_path, include_images):
    """
    Sends one pdf to Mistral cloud OCR model. 
    """

    client = Mistral(api_key=MISTRALAI_API_KEY)
    fileNoExt = os.path.splitext(pdf_file_path)[0]
    pdf_file = Path(pdf_file_path)

    # Verify PDF file exists
    assert pdf_file.is_file()

    # Send PDF to Mistral OCR
    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_file.stem,
            "content": pdf_file.read_bytes(),
        },
        purpose="ocr",
    )

    # Get URL for uploaded file
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

    # Process PDF and embedded images with OCR
    pdf_response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=include_images,
        retries = 30,
        timeout_ms = 600000,

    )

    if include_images == True:
        # Convert response to JSON
        response_json_dict = json.loads(pdf_response.model_dump_json())
        response_json_object = json.dumps(response_json_dict, indent=4)
        with open("{}.json".format(fileNoExt), 'w') as outfile:
            json.dump(response_json_object, outfile)

        # Convert Response to markdown
        response_markdown = get_combined_markdown(pdf_response)
        with open("{}.md".format(fileNoExt), 'w') as outfile:
            outfile.write(response_markdown)

    elif include_images == False:
        response_markdown = get_text_markdown(pdf_response)
        with open("{}.md".format(fileNoExt), 'w') as outfile:
            outfile.write(response_markdown)

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5, jitter=True)
def mistralPdfOcr_Retry(pdf_file_path):
    """
    Process OCR with retry and backoff
    """
    try:
        return mistralPdfOcr(pdf_file_path)
    except Exception as e:
        raise e #Reraise exception after

def processMistralPdfOcr(directory):
    """
    Sends a directory of pdf files to Mistral cloud OCR model. 
    """
    split_file_list = filesList(directory+"/split")
    currentFileCounter = 1
    totalFileCount = len(split_file_list)

    print("--> Cloud OCR processing starting!!")
    for file in split_file_list:
        # print(file)
        print(f"--> OCR processing: [{currentFileCounter} / {totalFileCount}] - {file}")
        mistralPdfOcr_Retry(file)
        currentFileCounter+= 1
        time.sleep(60)
    print("--> Cloud OCR processing done!!")

def breakdownPdfs(directory):
    """
    Breaks a directory of pdfs into multiple smaller page count files.
    """
    pageLimit = 50
    file_list = filesList(directory)
    os.mkdir(directory+"/split")
    
    print("--> PDF splitting starting!!")
    for file in file_list:
        breakdownPdf(file, pageLimit, directory)
    print("--> PDF splitting done!!")

def processPdfs(directory):
    """ 
    Process a directory of pdfs. Including breaking down the pdfs into smaller collection of pages and sending those to Mistral cloud OCR model.
    """
    breakdownPdfs(directory)
    processMistralPdfOcr(directory)

if __name__ == "__main__":
    main()
