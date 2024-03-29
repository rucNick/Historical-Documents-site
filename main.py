import asyncio
import os
import aiohttp

base_url = 'https://www.meckrodhistorical.com/DocumentViewPDF.asp?DocumentType={}&Instrument={}'


async def download_pdf(session, document_type, instrument, output_dir, known_sizes, retries=3, delay=1):
    url = base_url.format(document_type, instrument)
    for attempt in range(retries):
        async with session.get(url) as response:
            content_type = response.headers.get('Content-Type', '')
            if response.status == 200 and 'application/pdf' in content_type:
                pdf_data = await response.read()
                # Compute the hash of the PDF data
                file_size = len(pdf_data)
                if file_size in known_sizes:
                    print(f'Skipping duplicate {document_type} {instrument}.')
                    break  # Skip this file
                # Add new size to the set
                known_sizes.add(file_size)
                file_path = os.path.join(output_dir, f'{instrument}.pdf')
                with open(file_path, 'wb') as f:
                    f.write(pdf_data)
                print(f'Downloaded {document_type} {instrument}')
                break
            else:
                print(
                    f'Attempt {attempt + 1} failed for {document_type} {instrument}. Status code: {response.status}, '
                    f'Content-Type: {content_type}')
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
    else:
        print(f'Failed to download {document_type} {instrument} after {retries} attempts.')

async def main():
    known_sizes = set()  # Initialize the set for known file sizes
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                document_type = input(
                    'Please enter the document type (Deed, Old Deeds, Maps, Condos, Satisfactions), or press Enter to '
                    'quit: ').strip()
                if not document_type:
                    print("Exiting program.")
                    break

                book_num = input('Please enter the Book number: ').strip()
                if not book_num.isdigit():
                    raise ValueError("Book number must be numeric.")

                start_page = input('Please enter the starting Page number: ').strip()
                if not start_page.isdigit():
                    raise ValueError("Starting Page number must be numeric.")
                start_page = int(start_page)

                end_page = input('Please enter the ending Page number: ').strip()
                if not end_page.isdigit():
                    raise ValueError("Ending Page number must be numeric.")
                end_page = int(end_page)

                if start_page > end_page:
                    raise ValueError("Starting Page number must be less than or equal to Ending Page number.")

                output_dir = input('Please enter the directory path to save the PDF files: ').strip()
                os.makedirs(output_dir, exist_ok=True)

                for page_num in range(start_page, end_page + 1):
                    formatted_book_num = str(book_num).zfill(4)
                    formatted_page_num = str(page_num).zfill(4)
                    instrument = f'{formatted_book_num}{formatted_page_num}'
                    await download_pdf(session, document_type, instrument, output_dir, known_sizes)

                # Clear the known_sizes set after processing a range of pages
                known_sizes.clear()
                print('-' * 50)

            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break  # or continue, depending on desired behavior

    print('Program completed!')

if __name__ == '__main__':
    asyncio.run(main())
