import os

def filesList(documentPath):
    """ 
    Returnss a list of files in directory storted abc numbers, capital then lower case.
    """
    filesList = os.listdir(documentPath)
    filesList.sort()

    return [documentPath + "/" + x  for x in filesList if os.path.isfile(os.path.join(documentPath, x))]

def fileMoveToAdded(file):
    """
    Moves file to the _added folder. 
    """
    addedFolder = "/_added/"
    fileName = os.path.basename(file)
    directoryName = os.path.dirname(file)
    fileMoveFolder = directoryName+addedFolder
    fileMoveFullName = directoryName+addedFolder+fileName

    # Check if _added folder exists and if not create it then move the file.  
    if os.path.isdir(fileMoveFolder) == True:
        os.rename(file, fileMoveFullName)
    else: 
        os.mkdir(fileMoveFolder)
        os.rename(file, fileMoveFullName)
