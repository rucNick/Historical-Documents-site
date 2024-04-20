import asyncio
import os
import aiohttp

base_url = 'https://www.meckrodhistorical.com/DocumentViewPDF.asp?DocumentType={}&Instrument={}'

async def download_pdf(session, document_type, instrument, output_dir, last_size, retries=3, delay=1):
    url = base_url.format(document_type, instrument)
    for attempt in range(retries):
        async with session.get(url) as response:
            content_type = response.headers.get('Content-Type', '')
            if response.status == 200 and 'application/pdf' in content_type:
                pdf_data = await response.read()
                file_size = len(pdf_data)
                if file_size == last_size:
                    print(f'Skipping duplicate {document_type} {instrument}.')
                    return last_size  # Return the same last size to indicate skipping
                file_path = os.path.join(output_dir, f'{instrument}.pdf')
                with open(file_path, 'wb') as f:
                    f.write(pdf_data)
                print(f'Downloaded {document_type} {instrument}')
                return file_size  # Return the new file size after successful download
            else:
                print(f'Attempt {attempt + 1} failed for {document_type} {instrument}. Status code: {response.status}, Content-Type: {content_type}')
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
    else:
        print(f'Failed to download {document_type} {instrument} after {retries} attempts.')
        return last_size  # Return the last known size even if download fails

async def main():
    async with aiohttp.ClientSession() as session:
        document_type = input('Please enter the document type (Deed, Old Deeds, Maps, Condos, Satisfactions), or press Enter to quit: ').strip()
        if not document_type:
            print("Exiting program.")
            return

        mode = input("Enter '1' to download a range of pages in a specific book, '2' to process a range of books: ").strip()

        try:
            if mode == '1':
                book_num = input('Please enter the specific BOOK number: ').strip()
                start_page = int(input('Please enter the starting PAGE number: ').strip())
                end_page = int(input('Please enter the ending PAGE number: ').strip())

                if start_page > end_page:
                    raise ValueError("Starting page number must be less than or equal to ending page number.")

                formatted_book_num = str(book_num).zfill(4)
                output_dir = os.path.join('Books', f'Book_{formatted_book_num}')
                os.makedirs(output_dir, exist_ok=True)
                last_size = 0  # Initialize with 0 to indicate no file has been processed yet

                for page_num in range(start_page, end_page + 1):
                    formatted_page_num = str(page_num).zfill(4)
                    instrument = f'{formatted_book_num}{formatted_page_num}'
                    last_size = await download_pdf(session, document_type, instrument, output_dir, last_size)

            elif mode == '2':
                start_book = int(input('Please enter the starting BOOK number: ').strip())
                end_book = int(input('Please enter the ending BOOK number: ').strip())

                if start_book > end_book:
                    raise ValueError("Starting book number must be less than or equal to ending book number.")

                for book_num in range(start_book, end_book + 1):
                    formatted_book_num = str(book_num).zfill(4)
                    output_dir = os.path.join('Books', f'Book_{formatted_book_num}')
                    os.makedirs(output_dir, exist_ok=True)
                    last_size = 0  # Reset last size for each book

                    start_page = 1
                    end_page = 700  # Assumed max 700 pages per book

                    for page_num in range(start_page, end_page + 1):
                        formatted_page_num = str(page_num).zfill(4)
                        instrument = f'{formatted_book_num}{formatted_page_num}'
                        last_size = await download_pdf(session, document_type, instrument, output_dir, last_size)

                    print('-' * 50)

        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        print('Program completed!')

if __name__ == '__main__':
    asyncio.run(main())
