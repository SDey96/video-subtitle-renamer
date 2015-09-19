#!/usr/bin/python

import sys, getopt, os, re, glob

def separatorList():
    return ['-', '.', '_', ' ']

def replaceSeparators(inputString, desiredSeparator):
    outputString = inputString
    for separator in separatorList():
        outputString = outputString.replace(separator, desiredSeparator)

    return outputString

def extractCleanNameWithExtension(fullName):
    # purge file name of some ID in parentheses at the end if present (titulky.com subtitle format)
    result = re.search(r'^(.*?)(?:\([0-9]+\))?\.([a-z]+)$', fullName, re.I)
    if (result):
        name = result.group(1)
        extension = result.group(2)
        cleanName = name

        # in case file name contains Season/Episode part (TV show), stop there when looking for name
        result = re.search(r'^(.*?)(s[0-9]{1,2}e[0-9]{1,2})', name, re.I)
        if (result):
            cleanName = result.group(1) + result.group(2).upper()
        else:
            # file name contain some movie information (format, resolution, etc.), use that to detect actual movie name
            result = re.search(r'^(.*?)(hdtv|hd-?ts|xvid|hdrip|brrip|x264|480p|720p|1080p|ac3-ev)', name, re.I)
            if (result):
                cleanName = result.group(1)

        cleanName = cleanName[:-1] if cleanName.endswith(tuple(separatorList())) else cleanName

        return [cleanName, extension]
    else:
        return False

def selectFiles(types):
    files = []
    for selectedFiles in types:
        files.extend(glob.glob(selectedFiles))

    return files

def handleRename(oldFileName, newFileName, interactiveMode, message):
    if (interactiveMode):
        if confirm(message):
            renameFile(oldFileName, newFileName)
    else:
        renameFile(oldFileName, newFileName)
        print message

def confirm(message):
    proceed = raw_input(message + ", continue? (y/N) ")
    return proceed.lower() == 'y'

def renameFile(origName, newName):
    # os.rename(origName, newName)
    return

def renameVideoSubtitleFiles(fileName, filesRenamedTo):
    cleanName, extension = extractCleanNameWithExtension(fileName)

    if not cleanName:
        return

    # replace "-._ " separators for configured separator
    nameFormatted = replaceSeparators(cleanName, separator)

    newFileName = nameFormatted + '.' + extension

    # file name is already formatted correctly
    if newFileName == fileName:
        filesRenamedTo.append(fileName)
        print "File " + fileName + " is already in correct format, skipping..."
        return

    if (newFileName not in filesRenamedTo):
        filesRenamedTo.append(newFileName)

        message = "File will be renamed from " + fileName + " to " + newFileName
    else:
        i = 1
        _newFileName = newFileName
        newFileName = nameFormatted + "(" + str(i) + ")." + extension
        while (newFileName in filesRenamedTo):
            i += 1
            newFileName = nameFormatted + "(" + str(i) + ")." + extension

        filesRenamedTo.append(newFileName)

        message = "File will be renamed from " + fileName + " to " + newFileName + " (" + _newFileName + " already exists)" 

    handleRename(fileName, newFileName, interactiveMode, message)

def renameFiles(separator, interactiveMode, recursiveMode):
    # list of all subtitle filenames in current directory, sorted by length with shortest one first
    subtitleFiles = sorted(selectFiles(['*.srt', '*.sub']), key = len)

    # list of all movie/TV Show filenames in current directory, sorted by length with shortest one first
    videoFiles = sorted(selectFiles(['*.mkv', '*.avi', '*.mp4', '*.m4p', '*.m4v', '*.mpg', '*.mp2', '*.mpeg', '*.mpe', '*.mpv', '*.m2v']), key = len)

    filesRenamedTo = []

    # rename files
    if (len(videoFiles) == 1 and len(subtitleFiles) == 1):
        # only one video and subtitles file, I guess it is safe to rename video file based on clean subtitles file name
        videoFile = videoFiles[0]
        subtitleFile = subtitleFiles[0]

        renameVideoSubtitleFiles(subtitleFile, filesRenamedTo)

        newSubtitleFile = filesRenamedTo[0]
        result = re.search(r'^(.*?)\.([a-z]+)$', newSubtitleFile, re.I)
        if result:
            name = result.group(1)

            result = re.search(r'^(.*?)\.([a-z]+)$', videoFile, re.I)
            if result:
                extension = result.group(2)
                newVideoFileName = name + '.' + extension

                message = "File will be renamed from " + videoFile + " to " + newVideoFileName

                handleRename(videoFile, newVideoFileName, interactiveMode, message)

    else:
        videoSubtitlesFiles = subtitleFiles + videoFiles
        for _file in videoSubtitlesFiles:
            renameVideoSubtitleFiles(_file, filesRenamedTo)

    if (recursiveMode):
        # look for another directories within the current directory and continue renaming files in them
        for item in os.listdir('.'):
            if (os.path.isdir(item)):
                if (item.startswith('.')):
                    continue

                os.chdir(item)
                renameFiles(separator, interactiveMode, recursiveMode)
                os.chdir('..')

def usage():
    print "Usage: "+ sys.argv[0] + " [options]"
    print "Options:"
    print "\t-i, --interactive"
    print "\t\t Run interactively (you will have to confirm before each file gets renamed)"
    print "\t-r, --recursive"
    print "\t\t Rename files recursively in child directories"
    print "\t-s separator, --separator separator"
    print "\t\t Use separator for separating words in renamed file (default separator is '-')"

def main(separator, interactiveMode, recursiveMode):
    #os.chdir('../testing')

    #renameFiles(separator, interactiveMode, recursiveMode)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hirs:', ['help', 'interactive', 'recursive', 'separator'])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    separator = '-'
    interactiveMode = False
    recursiveMode = False

    for option, value in opts:
        if option in ('-h', '--help'):
            usage();
            sys.exit(0)
        elif option in ('-i', '--interactive'):
            interactiveMode = True
        elif option in ('-r', '--recursive'):
            recursiveMode = True
        elif option in ('-s', '--separator'):
            separator = value

    main(separator, interactiveMode, recursiveMode)