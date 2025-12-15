import csv
import os

# Percorso file input e output
folder = os.path.dirname(__file__)
input_csv = "6. Mappa OpenData/Incidenti_2016-2022.csv"
output_csv = "6. Mappa OpenData/incidenti_ripuliti.csv"

with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
	reader = csv.DictReader(infile, delimiter=';')
	writer = csv.writer(outfile, delimiter=';')
	writer.writerow(['latitudine', 'longitudine', 'grave'])
	for row in reader:
		lat = row.get('Lat') or row.get('lat') or row.get('latitudine')
		lon = row.get('Lon') or row.get('lon') or row.get('longitudine')
		feriti = row.get('Feriti', '0').strip()
		morti = row.get('Morti', '0').strip()
		try:
			feriti = int(feriti) if feriti else 0
		except ValueError:
			feriti = 0
		try:
			morti = int(morti) if morti else 0
		except ValueError:
			morti = 0
		grave = 1 if (feriti > 0 or morti > 0) else 0.5
		if lat and lon:
			writer.writerow([lat, lon, grave])
   
print("File ripulito creato:", output_csv)