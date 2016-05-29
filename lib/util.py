

def parseFilesToHierarchy(files):
	result = []

	for file in files:
		folders = file["fields"]["filename"].split("/")
		#lentgh minus 1 because the first element of array is '' since the string begins with '/'
		length = len(folders)-1
		current = 1

		#Parse folders (not the last one, which is normally a file)
		tmpResult = result
		while current < length:

			folder = folders[current]
			tmp = None
			for r in tmpResult:
				if folder in r["name"]:
					tmp = r
					break

			if not tmp:
				tmp = {
					"name": "/" + folder,
					"children": [],
					"type": "folder"
				}
				tmpResult.append(tmp)

			tmpResult = tmp["children"]
			current += 1

		#Parse the file itself (last one in path)
		tmpResult.append({
			"name": folders[current],
			"type": "file"				
		})

	return result