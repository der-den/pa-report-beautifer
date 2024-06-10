# pa-report-beautifer
Add and remove informations from PA HTML report.

usage: pa-report.py [-h] [-rs] [-at] [-tf TF] [-rap] input_file [output_file]

Make a beautiful version of a PA HTML report.

positional arguments:
  input_file   Path to HTML report file
  output_file  Path to output HTML file (optional)

options:
  -h, --help   show this help message and exit
  -rs          Remove "Source Info" sections.
  -at          Add transcription, search for *-ST.TXT files.
  -tf TF       Path to transcription files. Use with -at
  -rap         Remove "Path:" sections inside attachments. Call with -at