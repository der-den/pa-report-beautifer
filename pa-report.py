# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:37:23 2024

@author: denny, with support from ChatGPT ;-)
"""

import argparse
import os
from bs4 import BeautifulSoup

# Function to remove "Source Info" sections
def remove_source_info(input_file, output_file):
    # Load the HTML file
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML file
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <div class="stack"> elements
    divs = soup.find_all('div', class_='stack')

    for div in divs:
        # Check if "Source Info" is in the <span> element
        if div.find('span', string='Source Info: '):
            # Set display: none
            div['style'] = 'display: none;'

    # Save the modified HTML file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Function to add transcription and optionally remove the "Path:" block
def add_transcription(input_file, output_file, transcription_folder, remove_path):
    # Load the HTML file
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML file
    soup = BeautifulSoup(html_content, 'html.parser')

    # Collect all unique file names
    file_names = set()

    # Find all spans with "File name: "
    file_name_spans = soup.find_all('span', string='File name: ')
    
    for span in file_name_spans:
        # Find the sibling span that contains the file name
        file_name_span = span.find_next('span', class_='c3 s8', id='')
        if file_name_span:
            file_name = file_name_span.text.strip()
            if file_name.endswith('.opus'):
                file_names.add(file_name)
    
    print(f"Found {len(file_names)} unique file names.")

    imported_count = 0

    for file_name in file_names:
        transcription_file = os.path.join(transcription_folder, file_name.replace('.opus', '-ST.txt'))
        print(f"Looking for transcription file: {file_name}")
        
        if os.path.exists(transcription_file):
            with open(transcription_file, 'r', encoding='utf-8') as tf:
                transcription_content = tf.read().strip()
            
            # Find the span tag again to insert transcription after it
            for span in soup.find_all('span', string='File name: '):
                file_name_span = span.find_next('span', class_='c3 s8', id='')
                if file_name_span and file_name_span.text.strip() == file_name:
                    #print(f"Processing file name span: {file_name_span}")

                    # Optionally remove the "Path:" block
                    if remove_path:
                        # Find the parent div containing the "File name:" and then the sibling div with "Path:"
                        parent_div = span.find_parent('div', class_='stack')
                        path_div = parent_div.find_next_sibling('div', class_='stack')
                        if path_div and path_div.find('span', string='Path: '):
                            path_div['style'] = 'display: none;'

                    # Insert transcription
                    attachment_div = parent_div.find_previous('div', string='Attachments: ')
                    if attachment_div:
                        parent_div = attachment_div.find_parent('div', class_='stack')
                        if parent_div:
                            # Create a new <div class="stack"> for transcription
                            new_div = soup.new_tag('div', **{'class': 'stack'})
                            # Create the header for transcription
                            header_strong = soup.new_tag('strong')
                            header_span = soup.new_tag('span', **{'class': 'c3 s10', 'id': ''})
                            header_span.string = 'Transcription:'
                            header_strong.append(header_span)
                            new_div.append(header_strong)
                            # Add a line break
                            new_div.append(soup.new_tag('br'))
                            # Create the transcription content span
                            transcription_span = soup.new_tag('span', **{'class': 'c3 s8', 'id': ''})
                            transcription_span.string = transcription_content
                            new_div.append(transcription_span)
                            
                            # Insert the new div after the parent div
                            parent_div.insert_after(new_div)
                            imported_count += 1
                            break
                    else:
                        print(f"No attachment div found for file: {file_name}")

        else:
            print(f"Transcription file not found: {transcription_file}")

    # Save the modified HTML file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print(f"HTML file saved to {output_file}.")
    print(f"Total unique file names: {len(file_names)}")
    print(f"Successfully imported transcriptions: {imported_count}")

# Main function to handle command line arguments
def main():
    parser = argparse.ArgumentParser(description='Make a beautiful version of a PA HTML report.')
    parser.add_argument('input_file', help='Path to HTML report file')
    parser.add_argument('output_file', nargs='?', help='Path to output HTML file (optional)')
    parser.add_argument('-rs', action='store_true', help='Remove "Source Info" sections.')
    parser.add_argument('-at', action='store_true', help='Add transcription, search for *-ST.TXT files.')
    parser.add_argument('-tf', help='Path to transcription files. Use with -at')
    parser.add_argument('-rap', action='store_true', help='Remove "Path:" sections inside attachments. Call with -at')

    args = parser.parse_args()

    # Determine the output file name if not specified
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = args.input_file.rsplit('.', 1)[0] + '_changed.html'

    # Execute functionalities based on the provided arguments
    if args.rs:
        remove_source_info(args.input_file, output_file)
    elif args.at:
        if args.tf:
            add_transcription(args.input_file, output_file, args.tf, args.rap)
        else:
            print("Error: Transcription folder path is required for -at option.")
            parser.print_help()
    else:
        parser.print_help()

# Entry point of the script
if __name__ == '__main__':
    main()
