from bs4 import Tag


def parse_table(table: Tag):
    """Parse a table into a list of rows."""
    rows = []
    headers = []
    row: Tag
    cell: Tag
    for row in table.find_all('tr'):
        if row.find('th'):
            headers = [cell.text.strip() for cell in row.find_all('th')]
        else:
            rows.append([cell.text.strip() for cell in row.find_all('td')])
            
    return headers, rows