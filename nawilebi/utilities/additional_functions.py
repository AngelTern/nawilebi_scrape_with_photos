import re
from datetime import datetime

def extract_numbers(string):
    return re.sub(r'\D', '', string)

def process_car_model_autopia(car_model, car_mark):
    car_model_unchanged = car_model
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    
    car_model_without_mark = re.sub(re.escape(car_mark), '', car_model, flags=re.IGNORECASE).strip()
    
    car_model_adjusted = re.sub(year_pattern, '', car_model_without_mark).strip()

    return car_model_adjusted, car_model_unchanged



def process_part_full_name_autopia(part_full_name, car_model, car_mark):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    part_full_name_adjusted = re.sub(re.escape(car_model), '', part_full_name).strip()
    
    part_full_name_adjusted = re.sub(year_pattern, '', part_full_name_adjusted).strip()
    
    part_full_name_adjusted = re.sub(re.escape(car_mark), '', part_full_name_adjusted).strip()    
    
    part_full_name_adjusted = re.sub('-', '', part_full_name_adjusted).strip()
    
    return part_full_name_adjusted


def process_year_autopia(year):
    year_stripped = year.strip()
    current_year = datetime.now().year
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    match = re.search(year_pattern, year_stripped)

    start_year = None
    end_year = None

    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2)) if match.group(2) else current_year
    else:
        try:
            start_year = int(year_stripped)
            end_year = current_year
        except ValueError:
            pass

    return start_year, end_year
    
def get_digits_after_last_slash(string):
    match = re.search(r"/(\d+)(?=[^/]*$)", string)
    if match:
        return match.group(1)
    return None

def get_digits_after_last_equal(string):
    match =re.search(r"=(\d+)(?=[^=]*$)", string)
    if match:
        return match.group(1)
    return None

def process_car_model_vgparts(car_model):
    match = re.search(r'(\d{4})\s*-\s*(\d{4})', car_model)
    
    if match:
        year = f"{match.group(1)}-{match.group(2)}"
        car_model_cleaned = re.sub(r'\s*\d{4}\s*-\s*\d{4}', '', car_model).strip()
        car_model_cleaned = re.sub(r'-\s*$', '', car_model_cleaned).strip()
        car_model_cleaned = re.sub(r'\s*\(\)\s*$', '', car_model_cleaned).strip()
        if car_model_cleaned == "RAV-4":
            car_model_cleaned = "RAV4"
        return year, car_model_cleaned.upper()
    else:
        return None, re.sub(r'-\s*$', '', car_model).strip().upper()

def process_year_vgparts(year):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|\s*)')
    match = re.search(year_pattern, year)
    if match:
        start_year = match.group(1)
        end_year = match.group(2)
        if end_year:
            return int(start_year), int(end_year)
        else:
            return start_year, None
    else:
        return None, None
    
def process_car_model_topautoparts(car_model):

    match = re.search(r'(\d{2,4})-(\d{2,4}|ON)', car_model)
    
    if match:
        start_year = format_year(match.group(1))
        end_year = match.group(2)
        if end_year == 'ON':
            end_year = datetime.now().year
        else:
            end_year = format_year(end_year)
        
        year_range = f"{start_year}-{end_year}"
        car_model_cleaned = car_model.replace(match.group(0), '').strip()
        return year_range, car_model_cleaned, start_year, end_year
    else:
        return None, car_model, None, None
def process_car_part_full_topautoparts(car_part_full, car_model):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|\s*)')
    car_part_full = re.sub(year_pattern, '', car_part_full)
    if car_model:
        car_part_full = car_part_full.replace(car_model, '').strip()
    
    return car_part_full
def adjust_car_model_name_carparts(car_model):
    car_model_lowered = car_model.lower()
    car_model_adjusted = car_model_lowered.replace(" ", "-")
    return car_model_adjusted

def process_car_model_carparts(car_model):
    return re.sub(r'(\b\d{2,4}(?:-\d{2,4})?\b)', '', car_model).strip()

def process_part_full_name_carparts(part_full_name, car_model, car_mark):
    part_full_name_adjusted = re.sub(re.escape(car_model), '', part_full_name, flags=re.IGNORECASE).strip()
    part_full_name_adjusted = re.sub(re.escape(car_mark), '', part_full_name_adjusted, flags=re.IGNORECASE).strip()
    
    year_pattern = r'\b(\d{2,4})(?:-\d{2,4})?\b'
    
    year_match = re.search(year_pattern, part_full_name_adjusted)
    year = year_match.group(0) if year_match else None

    # Remove the year or year range from the part name
    part_full_name_final = re.sub(year_pattern, '', part_full_name_adjusted).strip()

    return part_full_name_final, year

def process_year_carparts(year):
    year = year.strip()
    
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|\s*)')
    match = year_pattern.search(year)
    
    if match:
        start_year = format_year(match.group(1))  
        end_year = match.group(2).strip() if match.group(2).strip() else None
        if end_year:
            end_year = format_year(end_year)  
    else:
        start_year = format_year(year)
        end_year = None

    return year, start_year, end_year

def process_car_model_vsauto(car_model):
    match = re.search(r'(\d{2,4}-\d{2,4})', car_model)
    if match:
        year_range = match.group(0)
        car_model = car_model.replace(year_range, '').strip()
        return year_range, car_model
    else:
        return None, car_model
    
def process_year_vsauto(year):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|\s*)')
    match = re.search(year_pattern, year)
    if match:
        start_year = match.group(1)
        end_year = match.group(2)
        return int(start_year), int(end_year)
    else: return None, None
    
def adjust_for_next_url_autotrans(car_mark, car_model):
    car_mark_adjusted = car_mark.lower()
    car_model_adjusted = re.sub(r"\s+", "-", car_model.lower())
    return car_mark_adjusted, car_model_adjusted

def process_and_clean_car_model_autotrans(car_model):
    current_year = datetime.now().year
    
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|ON|-)?', re.IGNORECASE)
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year_raw = match.group(2)
        
        if end_year_raw is None or end_year_raw.upper() == 'ON' or end_year_raw == '-':
            end_year = current_year
        else:
            end_year = format_year(end_year_raw)
        
        year_range = f"{start_year}-{end_year}"
    else:
        year_range = None

    cleaned_car_model = re.sub(year_pattern, '', car_model).strip()

    return start_year, end_year, cleaned_car_model


def process_part_full_name_carline(part_full_name, car_model, car_mark):
    part_full_name_1 = re.sub(car_model, '', part_full_name, flags=re.IGNORECASE).strip()
    part_full_name_2 = re.sub(car_mark, '', part_full_name_1, flags=re.IGNORECASE).strip()
    year_pattern = re.compile(r'(\d{2,4})')
    part_full_name_adjusted = re.sub(year_pattern, '', part_full_name_2).replace('-', '').strip()
    return part_full_name_adjusted
    
def clean_car_model_carline(car_model, car_mark):
    if car_mark == "CHEVROLET":
        car_model_adjusted = re.sub("CHEVY", '', car_model).strip()
    else:
        car_model_adjusted = re.sub(car_mark, '', car_model).strip()
    year_pattern = re.compile(r'\d{2,4}')
    match = year_pattern.search(car_model)
    if match:
        year_string = match.group()
        return year_string, re.sub(year_string, '', car_model_adjusted).strip()
    return None, car_model

def process_kia_carline(part_full_name):
    pattern_1 = re.compile(r"(SOUL 2009)")
    pattern_2 = re.compile(r"(CERATO)")
    
    match_1 = pattern_1.search(part_full_name)
    match_2 = pattern_2.search(part_full_name)
    
    if match_1:
        car_model = match_1.group()
        return car_model, re.sub(car_model, '', part_full_name).replace('-', '').strip()
    
    elif match_2:
        car_model = match_2.group()
        return car_model, re.sub(car_model, '', part_full_name).replace('-', '').strip()
    
    return None, part_full_name

def process_year_partscorner(year):
    year_pattern = re.compile(r'(\d{2,4})\s*[-–]\s*(\d{2,4})?|(\d{2,4})\s*[-–]\s*$')
    match = year_pattern.search(year)

    start_year = None
    end_year = None
    current_year = datetime.now().year

    if match:
        if match.group(1) and match.group(2):
            start_year = format_year(match.group(1))
            end_year = format_year(match.group(2))
        elif match.group(3):

            start_year = format_year(match.group(3))
            end_year = current_year

    return start_year, end_year


def process_year_goparts(car_model):
    current_year = datetime.now().year
    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{2,4})|(\d{4})\s*[-]\s*$|(\d{4})\b')
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    year_range = None

    if match:
        if match.group(1) and match.group(2):
            start_year = format_year(match.group(1))
            end_year = format_year(match.group(2))
            year_range = f"{start_year}-{end_year}"
        
        elif match.group(3):
            start_year = format_year(match.group(3))
            end_year = current_year
            year_range = f"{start_year}-{end_year}"

        elif match.group(4):
            start_year = format_year(match.group(4))
            end_year = current_year
            year_range = f"{start_year}-{end_year}"

        car_model = re.sub(match.group(0), '', car_model).strip()
    
    return car_model, start_year, end_year, year_range
    
def process_part_full_name_goparts(part_full_name, car_model, car_mark):
    part_prefix_pattern = re.compile(r'^\d{2,3}\s*[-–]?\s*')
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4})|(\d{2,4})\s*[-]\s*$')
    
    match = year_pattern.search(part_full_name)
    
    car_model_pattern = re.compile(re.escape(car_model), re.IGNORECASE)
    car_mark_pattern = re.compile(re.escape(car_mark), re.IGNORECASE)

    part_full_name = re.sub(part_prefix_pattern, '', part_full_name)

    match_car_model = car_model_pattern.search(part_full_name)
    if match_car_model:
        part_full_name = re.sub(match_car_model.group(0), '', part_full_name).strip()

    match_car_mark = car_mark_pattern.search(part_full_name)
    if match_car_mark:
        part_full_name = re.sub(match_car_mark.group(0), '', part_full_name).strip()

    if match:
        part_full_name = re.sub(match.group(0), '', part_full_name).strip()

    return re.sub('-', '', part_full_name).strip()

def translate_car_model_geoparts(car_model):
    georgian_to_english = {
        'ᲯᲔᲢᲐ': 'JETTA',
        'ᲞᲐᲡᲐᲢᲘ': 'PASSAT'
    }
    return georgian_to_english.get(car_model, car_model.upper())

def process_car_model_geoparts(car_model, car_mark):
    car_model = re.sub(re.escape(car_mark), '', car_model).strip()
    
    year_pattern = re.compile(r'(\d{4}|\d{2})\s*[-–]{1,2}\s*(\d{4}|\d{2})?|(\d{4}|\d{2})\s*[-]{0,1}$')
    match = year_pattern.search(car_model)

    start_year = None
    end_year = None
    year_range = None
    current_year = datetime.now().year

    if match:
        if match.group(1) and match.group(2):
            start_year = format_year(match.group(1))
            end_year = format_year(match.group(2))
            year_range = f"{start_year}-{end_year}"
        elif match.group(3):
            start_year = format_year(match.group(3))
            end_year = current_year
            year_range = f"{start_year}-{end_year}"

        car_model = re.sub(match.group(0), '', car_model).strip()

    return translate_car_model_geoparts(car_model), start_year, end_year, year_range
    
def process_car_model_zuparts(car_model):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4})')
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    year_range = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2))
        year_range = f"{start_year}-{end_year}"
        
        car_model = re.sub(match.group(0), '', car_model).strip()
    
    return car_model, start_year, end_year, year_range

def process_year_newparts(year):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4})')
    match = year_pattern.search(year)
    
    start_year = None
    end_year = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2))
        year_range = f"{start_year}-{end_year}"
        
    return year_range, start_year, end_year

import re

def process_car_model_newparts(car_model):
    engine_size_pattern = r'\d+(\.\d+)?L'
    cleaned_model = re.sub(engine_size_pattern, '', car_model).strip().upper()
    
    return cleaned_model if cleaned_model != car_model else car_model

def process_car_model_bgauto(car_model, car_mark):
    car_model = re.sub(car_mark, '', car_model).strip()

    current_year = datetime.now().year

    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{2,4}|ON)?')
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    year = None

    if match:
        start_year = format_year(match.group(1))

        end_year_str = match.group(2)
        if end_year_str and end_year_str.upper() == 'ON':
            end_year = current_year
        else:
            end_year = format_year(end_year_str) if end_year_str else current_year

        year = f"{start_year}-{end_year}"

        car_model = re.sub(year_pattern, '', car_model).strip()

    return car_model, start_year, end_year, year
    
def process_part_full_name_bgauto(part_full_name):
    year_pattern = re.compile(r'\d{4}\s*-\s*(\d{4})?')
    
    if year_pattern.search(part_full_name):
        cleaned_name = re.sub(year_pattern, '', part_full_name).strip()
    else:
        cleaned_name = part_full_name

    return cleaned_name
    
def process_year_proauto(year):
    year_pattern = re.compile(r'(\d{4})(?:\s*-\s*(\d{4}))?')
    match = year_pattern.search(year)
    
    start_year = None
    end_year = None
    year_result = year
    
    if match:
        start_year = format_year(match.group(1))

        end_year = format_year(match.group(2)) if match.group(2) else datetime.now().year

        year_result = f"{start_year}-{end_year}"
        
        year = re.sub(year_pattern, '', year).strip()

    return start_year, end_year, year_result

def process_car_model_proauto(car_model, car_mark):
    car_model = re.sub(car_mark, '', car_model)
    
    current_year = datetime.now().year

    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4})?')
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    year = None

    if match:
        start_year = format_year(match.group(1))

        end_year = format_year(match.group(2)) if match.group(2) else current_year

        year = f"{start_year}-{end_year}"

        car_model = re.sub(year_pattern, '', car_model).strip().upper()

    return car_model.upper(), start_year, end_year, year    
    
def process_car_model_crossmotors(car_model):
    current_year = datetime.now().year

    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4})?')
    match = year_pattern.search(car_model)
    
    start_year = None
    end_year = None
    year = None

    if match:
        start_year = format_year(match.group(1))

        end_year = format_year(match.group(2)) if match.group(2) else current_year

        year = f"{start_year}-{end_year}"

        car_model = re.sub(year_pattern, '', car_model).strip()

    return car_model, start_year, end_year, year

def process_car_model_autogama(car_model):
    car_mark_list = ["SUBARU", "HYUNDAI", "KIA", "NISSAN", "TOYOTA", "BMW"]
    car_mark = None

    car_model_upper = car_model.upper()

    for mark in car_mark_list:
        if mark in car_model_upper:
            car_mark = mark
            car_model = car_model_upper.replace(mark, '').strip()
            break

    current_year = datetime.now().year

    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4})?')
    match = year_pattern.search(car_model)

    start_year = None
    end_year = None
    year = None

    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2)) if match.group(2) else current_year
        year = f"{start_year}-{end_year}"

        car_model = year_pattern.sub('', car_model).strip()

    return car_mark, car_model, start_year, end_year, year


def process_part_full_name_autogama(part_full_name):
    price_pattern = re.compile(r'(\d+)\s*₾')

    match = price_pattern.search(part_full_name)

    price = None
    name = part_full_name

    if match:
        price = int(match.group(1))
        name = price_pattern.sub('', part_full_name).strip()

    return name, price


import re
from datetime import datetime

def process_part_full_name_apgparts(part_full_name, car_model):
    # List of car marks
    car_mark_list = ["TOYOTA", "HYUNDAI", "MAZDA"]
    
    # Clean and format car_model
    car_model = car_model.strip().upper()
    
    # Define the year pattern to detect year ranges
    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4})?')
    
    # Remove the year range from the car_model
    car_model_cleaned = re.sub(year_pattern, '', car_model).strip()

    car_mark = None

    # Find the car mark in the part_full_name
    for mark in car_mark_list:
        if mark in part_full_name.upper():
            car_mark = mark
            # Remove car mark from part_full_name
            part_full_name = re.sub(mark, '', part_full_name, flags=re.IGNORECASE).strip()
            break

    # Remove the car model from part_full_name
    part_full_name_cleaned = re.sub(re.escape(car_model_cleaned), '', part_full_name, flags=re.IGNORECASE).strip()
    
    # Remove any dashes or multiple spaces
    part_full_name_cleaned = re.sub(r'[-–]', '', part_full_name_cleaned).strip()
    part_full_name_cleaned = re.sub(r'\s+', ' ', part_full_name_cleaned).strip()

    # Remove the year from part_full_name
    part_full_name_cleaned = re.sub(r'\d{4}', '', part_full_name_cleaned).strip()

    # Handle the years in the car_model
    match = year_pattern.search(car_model)
    start_year = end_year = year = None
    current_year = datetime.now().year

    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2)) if match.group(2) else current_year
        year = f"{start_year}-{end_year}"

    return part_full_name_cleaned, car_mark, car_model_cleaned, start_year, end_year, year

def process_in_stock_pp(in_stock):
    if in_stock:
        in_stock_int = int(in_stock)
        if in_stock_int !=0:
            in_stock = True
        else: in_stock = False
    return in_stock

def process_year_pp(year_string_list):
    year_string_list = [year.strip() for year in year_string_list if year.strip()]
    
    current_year = datetime.now().year
    year_pattern = re.compile(r'(\d{4})\s*[-–]\s*(\d{4}|PRSS)?')

    for year_string in year_string_list:
        if year_string:
            match = year_pattern.search(year_string)
            
            if match:
                start_year = int(match.group(1))
                end_year_str = match.group(2)
                
                if end_year_str == "PRSS" or end_year_str is None:
                    end_year = current_year
                else:
                    end_year = int(end_year_str)
                
                year = f"{start_year}-{end_year}"
                return year, start_year, end_year
    
    return None, None, None


def process_car_model_pp(car_model, car_mark):
    if isinstance(car_model, list):
        car_model = ' '.join(car_model).strip()
    
    car_model = re.sub(r'\s+', ' ', car_model).strip()

    if car_mark in car_model:
        car_model = re.sub(car_mark, '', car_model).strip().upper()
    
    return car_model
            
def procees_price_pp(price):
    if isinstance(price, list):
        price = ' '.join(price).strip()
        
    return parse_price(price)

def extract_id_mmauto(url):
    match = re.search(r'/vehicle/(\d+)/', url)
    if match:
        vehicle_id = match.group(1)
        return vehicle_id
    else: return None

def process_part_full_name_pp(part_full_name):
    words = re.split(r'\s*,\s*|\s+', part_full_name)
    
    if len(words) == 2:
        if words[0].lower() == words[1].lower():
            return words[0]
    
    return part_full_name

def process_car_model_mmauto(car_model):
    
    current_year = datetime.now().year
    year_pattern = re.compile(r'(\d{4})\s*[-–]\s*(\d{4}|PRSS)?')


    match = year_pattern.search(car_model)
    
    if match:
        car_model = re.sub(year_pattern, '', car_model).strip()
        car_model = re.sub('-', '', car_model).strip()
        start_year = int(match.group(1))
        end_year_str = match.group(2)
        
        if end_year_str == "PRSS" or end_year_str is None:
            end_year = current_year
        else:
            end_year = int(end_year_str)
        
        year = f"{start_year}-{end_year}"
        return car_model.upper(), year, start_year, end_year
    
    return car_model, None, None, None

def process_in_stock(in_stock_list):
    in_stock_list = [in_stock.strip() for in_stock in in_stock_list if in_stock.strip()]
    
    in_stock_string = ' '.join(in_stock_list).strip()
    
    if "მარაგშია" in in_stock_list:
        in_stock = True
    elif "არ არის მარაგში" in in_stock_list:
        in_stock = False
    elif "გზაშია" in in_stock_list:
        in_stock = False
        
    if in_stock == True or in_stock == False:
        return in_stock
    else: return None
    

def process_car_model_otoparts(car_model, car_mark):
    car_model = re.sub(car_mark, "", car_model, flags=re.IGNORECASE).strip()
    current_year = datetime.now().year
    
    year_pattern = re.compile(r'(\d{2,4})\s*[-–]\s*(\d{4}|ON)?')
    
    match = year_pattern.search(car_model)
    
    if match:
        car_model = re.sub(year_pattern, '', car_model).strip()
        car_model = re.sub('-', '', car_model).strip()
        #car_model = re.sub('-', '', car_model).strip()
        car_model = re.sub(r'[\u200b\uFEFF]', '', car_model).strip()
        start_year = format_year(match.group(1))
        end_year_str = match.group(2)
        
        if end_year_str == "ON" or end_year_str is None:
            end_year = current_year
        else:
            end_year = format_year(end_year_str)
        
        year = f"{start_year}-{end_year}"
        return car_model.upper(), year, start_year, end_year
    
    return car_model, None, None, None

def adjust_car_name_for_url_megaauto(string):
    string = string.lower()

    string = re.sub(r'\s+', '-', string)

    string = re.sub(r'[()]', '', string)

    string = re.sub(r'[^a-z0-9-]', '', string)

    return string

def process_car_model_megaauto(car_model, car_mark):
    car_model = re.sub(car_mark, "", car_model, flags=re.IGNORECASE).strip()

    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4}|\s*)')
    
    match = year_pattern.search(car_model)
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2))
        year = match.group(0)
        
        return car_model, start_year, end_year, year
    
    return car_model, None, None, None
        

'''---------------------------------------------------------'''

def format_year(year):
    if year is None:
        return None
    year = int(year)
    if year < 100:
        if year >= 50:
            return 1900 + year
        else:
            return 2000 + year
    return year


import re

def parse_price(value):
    if isinstance(value, (int, float)):
        return value  
    
    if not isinstance(value, str):
        return None
    
    cleaned_string = re.sub(r'[^\d.,]', '', value)
    
    if not cleaned_string:
        return None
    
    cleaned_string = cleaned_string.replace(',', '.')
    
    try:
        return float(cleaned_string)
    except ValueError:
        return None
