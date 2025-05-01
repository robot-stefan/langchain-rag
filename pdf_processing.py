from pypdf import PdfReader, PdfWriter
from pathlib import Path
from mistralai import Mistral, DocumentURLChunk, ImageURLChunk, TextChunk
from mistralai.models import OCRResponse
from config import configSetting
from configCloud import MISTRALAI_API_KEY
from populate_database import filesList

import json, os, re, time, backoff, argparse

def main():
    """
    Pdf processing is for splitting up large pdfs for use with cloud OCR tools such as those provided by mistral. Some code in this has been taken from mistrals ocr demo notebook. Cloud OCR tool will generate a json and md file of the pdf. 
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
        for img in page.images:
            image_data[img.id] = img.image_base64
        # Replace image placeholders with actual images
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)

def mistralPdfOcr(pdf_file_path):
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
        include_image_base64=True,
        retries = 30,
        timeout_ms = 600000
    )

    # Convert response to JSON
    response_json_dict = json.loads(pdf_response.model_dump_json())
    response_json_object = json.dumps(response_json_dict, indent=4)
    with open("{}.json".format(fileNoExt), 'w') as outfile:
        json.dump(response_json_object, outfile)

    # Convert Response to markdown
    response_markdown = get_combined_markdown(pdf_response)
    with open("{}.md".format(fileNoExt), 'w') as outfile:
        outfile.write(response_markdown)
    
    # return [response_json_object, response_markdown]

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
        mistralPdfOcr(file)
        currentFileCounter+= 1
        time.sleep(45)
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
