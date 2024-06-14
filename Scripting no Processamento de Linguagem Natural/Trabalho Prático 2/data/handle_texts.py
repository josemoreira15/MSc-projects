import re, os

os.makedirs('texts', exist_ok=True)

pattern = re.compile(r"INSERT INTO public.dreapp_documenttext VALUES\s*\((.*?)\);\s*", re.IGNORECASE | re.DOTALL)

chunk_size = 1024 * 1024
buffer = ""

with open('2024-04-07-DRE_dump.sql', 'r') as file:
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        buffer += chunk
        
        matches = pattern.findall(buffer)
        if matches:
            for match in matches:
                values = match.split(',', 4)
                filename = values[1].strip()
                content = values[4][2:-1].strip()

                with open(f'texts/{filename}.txt', 'w') as out_file:
                    out_file.write(content)
                
            # Keep only the last part of the buffer that might contain an incomplete match
            buffer = buffer[-len(chunk):]
        
        elif 'public.dreapp_document' in buffer and 'INSERT INTO public.dreapp_documenttext' not in buffer:
            buffer = ""
        


# Handle any remaining buffer content
matches = pattern.findall(buffer)
if matches:
    for match in matches:
        values = match.split(',', 4)
        filename = values[1].strip()
        content = values[4][2:-1].strip()
        
        with open(f'texts/{filename}.txt', 'w') as out_file:
            out_file.write(content)