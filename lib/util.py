def _parseFiles(file, result):
    #lentgh minus 1 because the first element of array is '' since the string begins with '/'
    
    folders = file.filename.split("/")
    length = len(folders)-1
    current = 1

    tmpResult = result
    #Parse folders (not the last one, which is normally a file)
    while current < length:

        folder = folders[current]
        tmp = None
        for r in tmpResult:
            if "/" + folder == r["name"]:
                tmp = r
                break

        if not tmp:
            tmp = {
                "name": "/" + folder,
                "children": [],
                "type": "folder",
                "id": file.id
            }
            tmpResult.append(tmp)

        tmpResult = tmp["children"]
        current += 1

    #Parse the file itself (last one in path)
    tmpResult.append({
        "name": folders[current],
        "type": "file"              
    })


def parseFilesToHierarchy(files):
    result = []
    tmpResult = []

    for file in files:
        #folders = file[0][0].split("/")
        _parseFiles(file, result)


    return result