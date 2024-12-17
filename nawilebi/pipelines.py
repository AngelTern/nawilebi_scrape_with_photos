
from datetime import datetime
import mysql.connector
from itemadapter import ItemAdapter
import logging
import re
#from utilities.additional_functions import *
from scrapy.exceptions import DropItem
from dotenv import load_dotenv
import os
load_dotenv()

'''class NawilebiPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        in_stock_value = adapter.get("in_stock")

        if isinstance(in_stock_value, bool):
            adapter["in_stock"] = in_stock_value
        elif isinstance(in_stock_value, str):
            in_stock_value = in_stock_value.strip()
            if in_stock_value == "მარაგშია":
                adapter["in_stock"] = True
            else:
                adapter["in_stock"] = False
        else:
            adapter["in_stock"] = False

        field_names = adapter.field_names()

        for field_name in field_names:
            value = adapter.get(field_name)

            if isinstance(value, str):
                adapter[field_name] = value.strip()
            if field_name == "price":
                adapter[field_name] = parse_price(value)
            if field_name == "original_price":
                if value is not None:
                    adapter[field_name] = parse_price(value)

        return item
'''
class NawilebiPipeline:

    phone_map = {
        "https://apgparts.ge/": "555 21 21 96",
        "https://autogama.ge/": "593 10 08 78, 557 67 72 01, 568 82 93 33, 551 87 77 75",
        "https://autopia.ge": "0322 233 133",
        "https://autotrans.ge/": "511 30 13 03",
        "https://bgauto.ge/": "574 73 67 57",
        "https://carline.ge/": "514 22 98 98",
        "https://car-parts.ge": "577 12 73 76",
        "https://www.crossmotors.ge/": "595 10 18 02",
        "https://geoparts.ge/": "596 80 20 00",
        "https://goparts.ge/ge": "577 01 20 06",
        "https://mmauto.ge/": "593 27 79 16, 599 38 21 18",
        "https://newparts.ge/": "599 84 88 45",
        "https://partscorner.ge/": "591 93 07 41",
        "https://pp.ge/": "322 80 13 13, 591 22 99 33",
        "https://pro-auto.ge/": "596 27 82 78, 571 00 00 71",
        "https://soloauto.ge/": "555 20 20 50",
        "https://topautoparts.ge/": "599 92 07 52",
        "https://vgparts.ge/": "555 74 41 11",
        "https://vsauto.ge/": "596 10 31 03",
        "https://zupart.ge/ka": "555 52 24 90",
        "https://otoparts.ge/": "577 54 51 74",
        "https://megaautoparts.ge/": "568 68 55 36",
        "https://www.autotagi.ge/": "511 17 51 75"
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        part_full_name = adapter.get("part_full_name")

        # Assign phone number based on website
        website = item.get('website')

        if website in self.phone_map:
            item['phone'] = self.phone_map[website]
        else:
            spider.logger.info(f'No phone number found for website: {website}')

        car_mark = adapter.get("car_mark")
        if car_mark:
            adapter["car_mark"] = car_mark.upper()

        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"] = car_model.upper()

        return item


                    
        

class YearProcessPipeline:
    def process_item(self, item, spider):
        year_str = item.get('year', None)
        start_year = None
        end_year = None

        if year_str:
            year_str = year_str.strip()
            if '-' in year_str:
                parts = year_str.split('-')
                if len(parts) == 2:
                    start_year_str = parts[0].strip()
                    try:
                        start_year = int(start_year_str)
                    except ValueError:
                        start_year = None

                    end_year_str = parts[1].strip()
                    if end_year_str == '':
                        end_year = datetime.now().year
                    else:
                        try:
                            end_year = int(end_year_str)
                        except ValueError:
                            end_year = None
            else:
                try:
                    start_year = int(year_str)
                    end_year = start_year
                except ValueError:
                    start_year = None
                    end_year = None

        item['start_year'] = start_year
        item['end_year'] = end_year

        return item



import mysql.connector
from mysql.connector import Error
from datetime import datetime

class SaveToMySQLPipeline:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=''
        )
        self.cur = self.conn.cursor()

    def check_and_truncate(self, website):
        today = datetime.now().strftime('%Y-%m-%d')
        control_file_path = 'control_file.txt'
        control_data = {}

        try:
            with open(control_file_path, 'r') as file:
                for line in file:
                    if line.strip() and '=' in line:
                        site, date = line.strip().split('=', 1)
                        control_data[site.strip()] = date.strip()

        except FileNotFoundError:
            open(control_file_path, 'w').close()

        if control_data.get(website) != today:
            self.cur.execute('DELETE FROM nawilebi WHERE website = %s', (website,))
            self.conn.commit()
            control_data[website] = today

            with open(control_file_path, 'w') as file:
                for site, date in control_data.items():
                    file.write(f"{site} = {date}\n")

    def process_item(self, item, spider):
        website = item.get('website', '')

        self.check_and_truncate(website)

        self.cur.execute('''
            INSERT INTO nawilebi(
                part_url, car_mark, car_model, part_full_name, alternative_name_1,
                alternative_name_2, alternative_name_3, alternative_name_4, alternative_name_5, alternative_name_6, 
                start_year, end_year, price, original_price,
                in_stock, city, website, phone
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            item.get('part_url', ''),
            item.get('car_mark', ''),
            item.get('car_model', ''),
            item.get('part_full_name', ''),
            item.get('alternative_name_1', ''),
            item.get('alternative_name_2', ''),
            item.get('alternative_name_3', ''),
            item.get('alternative_name_4', ''),
            item.get('alternative_name_5', ''),
            item.get('alternative_name_6', ''),
            item.get('start_year', None),
            item.get('end_year', None),
            item.get('price', 0),
            item.get('original_price', 0),
            item.get('in_stock', False),
            item.get('city', ''),
            item.get('website', ''),
            item.get('phone', '')
        ))

        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()


class AutopiaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        
        car_mark = adapter.get("car_mark")
        if car_mark:
            adapter["car_mark"] = car_mark.strip()
            
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], car_model_unchanged, adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_autopia(car_model, adapter.get("car_mark"))
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            part_full_name = re.sub(car_model_unchanged, "", part_full_name).strip()
            part_full_name = re.sub("-", "", part_full_name).strip()
            adapter["part_full_name"] = part_full_name
        
        return item

'''class AutopiaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        for field_name in field_names:
            value = adapter.get(field_name)
            
            if isinstance(value, str):
                adapter[field_name] = value.strip()

            if field_name == "car_mark":
                adapter[field_name] = value.upper().strip()
                
            elif field_name == "car_model":
                car_model_adjusted, car_model_unchanged = process_car_model_autopia(value, adapter.get("car_mark"))
                adapter[field_name] = car_model_adjusted
                
            elif field_name == "in_stock":
                if value == "modal-wrapper":
                    adapter[field_name] = True
                else:
                    adapter[field_name] = False
                
            elif field_name == "part_full_name":
                car_model_unchanged = adapter.get("car_model") if 'car_model' in adapter else ""
                adapter[field_name] = process_part_full_name_autopia(value, adapter.get("car_model"), adapter.get("car_mark"))
                
            elif field_name == "price":
                adapter[field_name] = parse_price(value)
            elif field_name == "year":
                adapter["start_year"], adapter["end_year"] = process_year_autopia(value)
                
        return item'''


class VgpartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == "car_model":
                year, car_model = process_car_model_vgparts(value)
                adapter["year"] = year
                adapter["car_model"] = car_model
            elif field_name == "year":
                adapter["start_year"], adapter["end_year"] = process_year_vgparts(value)
                
            if field_name == "car_mark":
                adapter[field_name] = value.upper()

        return item


class TopautopartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        
        year_range, car_model, start_year, end_year = None, None, None, None
        
        for field_name in field_names:
            value = adapter.get(field_name)

            if field_name == "car_model":
                year_range, car_model, start_year, end_year = process_car_model_topautoparts(value)
                adapter["start_year"] = int(start_year) if start_year else None
                adapter["end_year"] = int(end_year) if end_year else None
                adapter["year"] = year_range
                adapter["car_model"] = car_model

            if field_name == "part_full_name":
                adapter[field_name] = process_car_part_full_topautoparts(value, car_model)

            if field_name == "price":
                adapter[field_name] = parse_price(value)

        return item

class CarpartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        
        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == "car_model":
                adapter[field_name] = process_car_model_carparts(value)
            elif field_name == "part_full_name":
                adapter[field_name], year_value = process_part_full_name_carparts(value, adapter.get("car_model"), adapter.get("car_mark"))
            elif field_name == "year":
                if value != None:
                    adapter["year"], start_year, end_year = process_year_carparts(value)
                    adapter["start_year"] = int(start_year) if start_year else None
                    adapter["end_year"] = int(end_year) if end_year else None
                else:
                    adapter["year"], start_year, end_year = process_year_carparts(year_value)
                    adapter["start_year"] = int(start_year) if start_year else None
                    adapter["end_year"] = int(end_year) if end_year else None
            elif field_name == "price":
                adapter[field_name] = parse_price(value)
            elif field_name == "in_stock":
                if value == "მარაგშია":
                    adapter[field_name] = 1
                else:
                    adapter[field_name] = 0

        return item

class VsautoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == "car_model":
                year, car_model = process_car_model_vsauto(value)
                adapter["year"] = year
                adapter["car_model"] = car_model
            elif field_name == "price":
                adapter[field_name] = float(value) if float(value) else None
            elif field_name == "year":
                adapter["start_year"], adapter["end_year"] = process_year_vsauto(value)
        return item


class AutotransPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        
        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == "car_model":
                start_year, end_year, cleaned_car_model = process_and_clean_car_model_autotrans(value)
                adapter["start_year"] = start_year
                adapter["end_year"] = end_year
                adapter["car_model"] = cleaned_car_model
            elif field_name == "price":
                adapter["price"] = parse_price(value)

        return item

class CarlinePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Process based on car_mark
        car_mark = adapter.get("car_mark")
        part_full_name = adapter.get("part_full_name")
        if car_mark and part_full_name:
            if car_mark == "KIA":
                adapter["car_model"], adapter["part_full_name"] = process_kia_carline(part_full_name)
        
        # Clean car_model and extract year
        car_model = adapter.get("car_model")
        if car_model:
            adapter["year"], adapter["car_model"] = clean_car_model_carline(car_model, adapter.get("car_mark"))

        # Process part_full_name again if necessary
        part_full_name_2 = adapter.get("part_full_name")
        if part_full_name_2:
            adapter["part_full_name"] = process_part_full_name_carline(part_full_name, adapter.get("car_model"), adapter.get("car_mark"))
        
        # Clean price if applicable
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)

        # Handle car model-specific logic based on car_mark and year
        year = adapter.get("year")
        car_mark = adapter.get("car_mark")
        car_model = adapter.get("car_model")

        if year and car_mark:
            if car_mark == "CHEVROLET":
                if car_model == "CRUZE":
                    if year == "2009":
                        adapter["start_year"] = 2009
                        adapter["end_year"] = 2014
                    elif year == "2015":
                        adapter["start_year"] = 2015
                        adapter["end_year"] = 2015
                    elif year == "2016":
                        adapter["start_year"] = 2016
                        adapter["end_year"] = 2018
                    elif year == "2019":
                        adapter["start_year"] = 2019
                        adapter["end_year"] = datetime.now().year
                elif car_model == "MALIBU":
                    if year == "2016":
                        adapter["start_year"] = 2016
                        adapter["end_year"] = 2018
                    elif year == "2019":
                        adapter["start_year"] = 2019
                        adapter["end_year"] = datetime.now().year
                elif car_model == "TRAX":
                    adapter["start_year"] = 2017
                    adapter["end_year"] = datetime.now().year
                elif car_model == "EQUINOX":
                    adapter["start_year"] = 2018
                    adapter["end_year"] = 2019
            elif car_mark == "FORD":
                if car_model == "FOCUS":
                    if year == "2012":
                        adapter["start_year"] = 2012
                        adapter["end_year"] = 2014
                    elif year == "2015":
                        adapter["start_year"] = 2015
                        adapter["end_year"] = datetime.now().year
                elif car_model == "FIESTA":
                    adapter["start_year"] = 2013
                    adapter["end_year"] = datetime.now().year
                elif car_model == "FUSION":
                    if year == "2013":
                        adapter["start_year"] = 2013
                        adapter["end_year"] = 2016
                    elif year == "2017":
                        adapter["start_year"] = 2017
                        adapter["end_year"] = 2018
                    elif year == "2019":
                        adapter["start_year"] = 2019
                        adapter["end_year"] = datetime.now().year
                elif car_model == "ESCAPE":
                    if year == "2013":
                        adapter["start_year"] = 2013
                        adapter["end_year"] = 2016
                    elif year == "2017":
                        adapter["start_year"] = 2017
                        adapter["end_year"] = 2019
                    elif year == "2020":
                        adapter["start_year"] = 2020
                        adapter["end_year"] = datetime.now().year
                elif car_model == "EXPLORER":
                    adapter["start_year"] = 2013
                    adapter["end_year"] = datetime.now().year
                elif car_model == "C-MAX":
                    adapter["start_year"] = 2013
                    adapter["end_year"] = datetime.now().year
                elif car_model == "ECOSPORT":
                    adapter["start_year"] = 2015
                    adapter["end_year"] = datetime.now().year
            elif car_mark == "TESLA":
                if car_model == "MODES 3":
                    if year == "2018":
                        adapter["start_year"] = 2018
                        adapter["end_year"] = 2020
                    elif year == "2021":
                        adapter["start_year"] = 2021
                        adapter["end_year"] = datetime.now().year
                elif car_model == "MODES Y":
                    adapter["start_year"] = 2020
                    adapter["end_year"] = datetime.now().year
            elif car_mark == "BUICK":
                if car_model == "ENCORE":
                    if year == "2013":
                        adapter["start_year"] = 2013
                        adapter["end_year"] = 2016
                    elif year == "2017":
                        adapter["start_year"] = 2017
                        adapter["end_year"] = datetime.now().year
            elif car_mark == "HYUNDAI":
                if car_model == "ELANTRA":
                    if year == "2011":
                        adapter["start_year"] = 2011
                        adapter["end_year"] = 2013
                    elif year == "2014":
                        adapter["start_year"] = 2014
                        adapter["end_year"] = 2015
                    elif year == "2016":
                        adapter["start_year"] = 2016
                        adapter["end_year"] = 2018
                    elif year == "2019":
                        adapter["start_year"] = 2019
                        adapter["end_year"] = 2021
                    elif year == "2022":
                        adapter["start_year"] = 2022
                        adapter["end_year"] = datetime.now().year
                elif car_model == "SONATA":
                    if year == "2011":
                        adapter["start_year"] = 2011
                        adapter["end_year"] = 2014
                    elif year == "2015":
                        adapter["start_year"] = 2015
                        adapter["end_year"] = 2017
                    elif year == "2018":
                        adapter["start_year"] = 2018
                        adapter["end_year"] = datetime.now().year
                elif car_model == "TUCSON":
                    if year == "2010":
                        adapter["start_year"] = 2010
                        adapter["end_year"] = 2015
                    elif year == "2016":
                        adapter["start_year"] = 2016
                        adapter["end_year"] = datetime.now().year
            elif car_mark == "MAZDA":
                if car_model == "3":
                    adapter["start_year"] = 2009
                    adapter["end_year"] = datetime.now().year
                elif car_model == "CX5":
                    adapter["start_year"] = 2014
                    adapter["end_year"] = datetime.now().year
            elif car_mark == "JEEP":
                if car_model == "LATITUDE":
                    adapter["start_year"] = 2014
                    adapter["end_year"] = datetime.now().year

        return item


class PartscornerPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == "year":
                adapter["start_year"], adapter["end_year"] = process_year_partscorner(value)
            elif field_name == "price":
                adapter["price"] = parse_price(value)
            elif field_name == "in_stock":
                if value == "მარაგშია":
                    adapter[field_name] = True
                else:
                    adapter[field_name] = False
            elif field_name == "car_mark":
                if value:
                    adapter[field_name] = value.upper()
            elif field_name == "car_model":
                if value and value == "akordi":
                    adapter[field_name] = "ACCORD"
                elif value and value == "hrv":
                    adapter[field_name] = "HR-V"
                else:
                    adapter[field_name] = value.upper()
                    
                
        return item
    
class GopartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            
            if isinstance(value, str):
                adapter[field_name] = value.strip()
                
            if field_name == "car_mark":
                if value == "B.M.W":
                    adapter[field_name] = re.sub(r'[^a-zA-Z]', '', value)
                elif value == "MERCEDES-BENZ":
                    adapter[field_name] = "MERCEDES"
            elif field_name == "car_model":
                adapter[field_name], adapter["start_year"], adapter["end_year"], adapter["year"] = process_year_goparts(value)
            elif field_name == "part_full_name":
                if value == "0- საქარე მინის გერმეტიკი 310მლ":
                    adapter[field_name] = "საქარე მინის გერმეტიკი 310მლ"
                else:
                    adapter[field_name] = process_part_full_name_goparts(value, adapter.get("car_model"), adapter.get("car_mark"))
            elif field_name == "in_stock":
                if value =="in_stock":
                    adapter[field_name] = 1
                else:
                    adapter[field_name] = 0
            elif field_name == "price":
                adapter[field_name] = parse_price(value)
            
        return item
    
class GeopartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        
        for field_name in field_names:
            value = adapter.get(field_name)

            if field_name == "car_mark" and value == "ᲢᲝᲘᲝᲢᲐ":
                
                adapter["car_mark"] = "TOYOTA"
                
            elif field_name == "car_model":
                adapter[field_name], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_geoparts(value, adapter.get("car_mark"))
            elif field_name in ["price", "original_price"]:
                adapter[field_name] = parse_price(value)


        return item
    
class ZupartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        car_model = adapter.get('car_model')
        if car_model:
            if "19980-05" in car_model:
                car_model = car_model.replace("19980-05", "1998-05")
            adapter['car_model'], adapter['start_year'], adapter['end_year'], adapter['year'] = process_car_model_zuparts(car_model)

        price = adapter.get('price')
        if price:
            adapter['price'] = parse_price(price)
        
        return item

class NewpartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
        
        year = adapter.get("year")
        if year:
            adapter["year"], adapter["start_year"], adapter["end_year"] = process_year_newparts(year)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"] = process_car_model_newparts(car_model)
        return item
    
class BgautoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_bgauto(car_model, adapter.get("car_mark"))
        
        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            adapter["part_full_name"] = process_part_full_name_bgauto(part_full_name)
        
        return item
    
class ProautoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        year = adapter.get("year")
        if year:
            adapter["start_year"], adapter["end_year"], adapter["year"] = process_year_proauto(year)
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
        
        original_price = adapter.get("original_price")
        if original_price:
            adapter["original_price"] = parse_price(original_price)
            
        
        return item
    
class SoloautoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_proauto(car_model, adapter.get("car_mark"))
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        car_mark = adapter.get("car_mark")
        if car_mark:
            car_mark = re.sub(r"/|\xa0", "", car_mark)
            adapter["car_mark"] = car_mark.upper()
            
        return item    
        
class SoloautoPipeline_2:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        car_mark = adapter.get("car_mark")
        if car_model and car_mark:
            adapter["car_model"] = re.sub(car_mark, '', car_model).strip().upper()
            
        return item
    
class CrossmotorsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_crossmotors(car_model)
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        return item
    
class AutogamaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            adapter["part_full_name"], adapter["price"] = process_part_full_name_autogama(part_full_name)

        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_mark"], adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_autogama(car_model)

        return item

    
class ApgpartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        part_full_name = adapter.get("part_full_name")
        
        if 'აქსესუარი 1' in part_full_name:
            raise DropItem(f"Dropping item with part_full_name: {part_full_name}")
        
        if part_full_name:
            adapter["part_full_name"], adapter["car_mark"], adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_part_full_name_apgparts(part_full_name, adapter.get("car_model"))
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"] = car_model.strip().upper()
        
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
        
        return item

class PpPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get('car_model')
        car_mark = adapter.get("car_mark")
        
        if car_model and car_mark:
            adapter["car_model"] = process_car_model_pp(car_model, car_mark)
            
        in_stock = adapter.get("in_stock")
        if in_stock:
            adapter["in_stock"] = process_in_stock_pp(in_stock)
            
        price = adapter.get("price")
        original_price = adapter.get("original_price")
        if price:
            adapter["price"] = procees_price_pp(price)
        if original_price:
            original_price_parsed = procees_price_pp(original_price)
            adapter["original_price"] = original_price_parsed if original_price_parsed and original_price_parsed != 0 else None
            
        year_list = adapter.get("year")
        if year_list:
            adapter["year"], adapter["start_year"], adapter["end_year"] = process_year_pp(year_list)
            
        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            adapter["part_full_name"] = process_part_full_name_pp(part_full_name)
            
            
        return item
            
            
class MmautoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["year"], adapter["start_year"], adapter["end_year"] = process_car_model_mmauto(car_model)
            
        in_stock = adapter.get("in_stock")
        if in_stock:
            adapter["in_stock"] = process_in_stock(in_stock)
            
        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            adapter["part_full_name"] = part_full_name.strip()
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
            
        return item
    
class OtopartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["year"], adapter["start_year"], adapter["end_year"] = process_car_model_otoparts(car_model, adapter.get("car_mark"))
            
        part_full_name = adapter.get("part_full_name")
        if part_full_name:
            adapter["part_full_name"] = re.sub(r"[-–]", "", part_full_name)
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        car_mark = adapter.get("car_mark")
        if car_mark:
            adapter["car_mark"] = car_mark.upper()
            
        return item
    
class MetaautopartsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"], adapter["year"] = process_car_model_megaauto(car_model, adapter.get("car_mark"))
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        return item
        
            

class AutotagioPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        car_model = adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"] = process_car_model_autotagi(car_model)
            
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        return item

class CarclubPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        part_full_name = adapter.get("part_full_name")
        start_year = adapter.get("start_year")
        end_year = adapter.get("end_year")
        if part_full_name:
            adapter["part_full_name"] = process_part_full_name_carclub(part_full_name, adapter.get("car_model"))
                
        if start_year:
            adapter["start_year"] = format_year(start_year)
            
        if end_year:
            adapter["end_year"] = format_year(end_year)
        
        price = adapter.get('price')
        if price:
            adapter["price"] = parse_price(price)
            
        return item

class MydubaiPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        price = adapter.get("price")
        if price:
            adapter["price"] = parse_price(price)
            
        car_model= adapter.get("car_model")
        if car_model:
            adapter["car_model"], adapter["start_year"], adapter["end_year"] = process_car_model_mydubai(car_model)
            
        return item

###---------------

def process_car_model_mydubai(car_model):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    match = re.search(year_pattern, car_model)
    current_year = datetime.now().year
    start_year = None
    end_year = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2)) if match.group(2) else current_year
        car_model = re.sub(year_pattern, '', car_model)
        
    return car_model, start_year, end_year

def process_year_carclub(year):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    match = re.search(year_pattern, year)
    current_year = datetime.now().year
    start_year = None
    end_year = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2)) if match.group(2) else current_year
        
    return start_year, end_year
    
def process_part_full_name_carclub(part_full_name, car_model):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    match = re.search(year_pattern, part_full_name)    
    
    part_full_name = re.sub(car_model, '', part_full_name).strip()
    
    if match:
        part_full_name = re.sub(year_pattern, '', part_full_name).strip()
        
        return part_full_name
    return part_full_name

def process_car_model_autotagi(car_model):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    match = re.search(year_pattern, car_model)
    current_year = datetime.now().year
    start_year = None
    end_year = None
    
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2)) if match.group(2) else current_year
        car_model = re.sub(year_pattern, '', car_model).strip()
        
        return car_model, start_year, end_year
    return car_model, start_year, end_year

import re
from datetime import datetime

def extract_numbers(string):
    return re.sub(r'\D', '', string)

'''def process_car_model_autopia(car_model, car_mark):
    car_model_unchanged = car_model
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    
    car_model_without_mark = re.sub(re.escape(car_mark), '', car_model, flags=re.IGNORECASE).strip()
    
    car_model_adjusted = re.sub(year_pattern, '', car_model_without_mark).strip()

    return car_model_adjusted, car_model_unchanged'''



def process_part_full_name_autopia(part_full_name, car_model, car_mark):
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    part_full_name_adjusted = re.sub(re.escape(car_model), '', part_full_name).strip()
    
    part_full_name_adjusted = re.sub(year_pattern, '', part_full_name_adjusted).strip()
    
    part_full_name_adjusted = re.sub(re.escape(car_mark), '', part_full_name_adjusted).strip()    
    
    part_full_name_adjusted = re.sub('-', '', part_full_name_adjusted).strip()
    
    return part_full_name_adjusted


def process_car_model_autopia(car_model, car_mark):
    car_model_unchanged = car_model
    year_pattern = re.compile(r'(\d{2,4})\s*-\s*(\d{0,4})')
    car_model_without_mark = re.sub(re.escape(car_mark), '', car_model, flags=re.IGNORECASE).strip()
    
    start_year = None
    end_year = None
    year = None
    current_year = datetime.now().year
    
    match = re.search(year_pattern, car_model_without_mark)
    if match:
        start_year = format_year(match.group(1))
        end_year = format_year(match.group(2)) if match.group(2) else current_year
        year = match.group(0)
        
        car_model_adjusted = re.sub(year_pattern, '', car_model_without_mark).strip()

        return car_model_adjusted, car_model_unchanged, start_year, end_year, year

    return car_model_without_mark, car_model_unchanged, start_year, end_year, year
    
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
    match = re.search(r'(\d{2,4}-\d{2,4}|\b\d{4}\b)', car_model)
    if match:
        year_range = match.group(0)
        # Remove the year or year range from the car_model string
        car_model = car_model.replace(year_range, '').strip()
        return year_range, car_model
    else:
        return None, car_model
    
def process_year_vsauto(year):
    year_pattern = re.compile(r'(\d{4})\s*-\s*(\d{4}|\s*)|\b(\d{4})\b')
    match = re.search(year_pattern, year)

    current_year = datetime.now().year

    if match:
        if match.group(1) and match.group(2):
            start_year = match.group(1)
            end_year = match.group(2) if match.group(2) else current_year
            return int(start_year), int(end_year)
        elif match.group(3):
            start_year = match.group(3)
            return int(start_year), current_year
    else:
        return None, None
    
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
    
    if "TESLA 3" in car_model:
        return "MODEL 3", "2017", "2024", "2017 - 2024"
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
    if "17- TESLA Model 3" in part_full_name:
        return re.sub("17- TESLA Model 3", '', part_full_name).strip()
    
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

