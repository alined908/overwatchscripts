import pandas as pd

def fix_map_guids():
    df = pd.read_csv('C:/Users/Daniel Lee/Desktop/Blizzard Stats/Season2/payload_guids_maps.tsv.gz', sep = '\t', compression = "gzip")

    for index, row in df.iterrows():
        us_only = row['map_name'].split("en_US")[1].split(',')[0].split(':')[1].replace('"', '')
        df.at[index, 'map_name'] = us_only
        print(us_only)

    df.to_csv("C:/Users/Daniel Lee/Desktop/Blizzard Stats/Season2/cleaned_map_guids.csv")

if __name__ == '__main__':
    fix_map_guids()
