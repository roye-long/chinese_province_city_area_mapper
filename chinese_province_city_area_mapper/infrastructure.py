# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 00:55:14 2018

@author: 燃烧杯
"""

import jieba,re

class Record:
    def __init__(self, line):
        from .domain import Location
        self.location = Location()
        index_dict={}
        #默认选取第一个遇到的省，市或者自治区
        for word in jieba.cut(line):
            if word == "上海市浦东新区":
                self.location.setPlace("上海市", SuperMap.CITY)
                self.location.setPlace("浦东新区", SuperMap.AREA)
                continue
            newword,word_type= SuperMap.getType(word)
            #print(word,word_type)
            if word_type and word_type in ['area','city','province','street'] :
                self.location.setPlace(newword, word_type)
                
                word_max_index=line.rindex(word)
                
                index_dict[word_max_index]=len(word)
        
        if len(list(index_dict.keys()))>0:
            #print(index_dict)
            minindx=min(list(index_dict.keys()))
            reline=line[minindx+index_dict[minindx]:]
        else:reline=line[0:]
        if reline.startswith('镇'):
            reline=reline.replace('镇','',1)
        elif reline.startswith('乡'):
            reline=reline.replace('乡','',1)
        elif reline.startswith('街'):
            reline=reline.replace('街','',1)
        #reline=reline.replace('省','').replace('市','').replace('区','').replace('县','')
        regx='[^\u4e00-\u9fa5 ,!?、，。！？\d\w]+'
        parttern = re.compile(regx)
        reline=parttern.sub('', reline)
        #print(reline)
        newreline,types=SuperMap.getType(reline)
        self.location.setPlace(newreline, types)
    def pca_map(self, umap):
         return self.location.pca_map(umap)
            
    
        

            

class SuperMap:
    from .mappers import area_city_mapper, city_province_mapper,\
                        province_country_mapper,street_area_mapper, rep_areas, \
                        lat_lon_mapper
    
    AREA = "area"
    CITY = "city"
    PROVINCE = "province"
    STRRET='street'
    DETAIL='detail'
    rep_area_set = set()
    
    @classmethod
    def getType(cls, word):
        if cls.area_city_mapper.get(word):
            return (word,cls.AREA)
        elif cls.city_province_mapper.get(word):
            return (word,cls.CITY)
        elif cls.province_country_mapper.get(word):
            return (word,cls.PROVINCE)
        elif cls.area_city_mapper.get(word+'区'):
            return (word+'区',cls.AREA)
        elif cls.area_city_mapper.get(word+'县'):
            return (word+'县',cls.AREA)
        elif cls.street_area_mapper.get(word+'镇'):
            return (word+'镇',cls.STRRET)
        elif cls.street_area_mapper.get(word+'乡'):
            return (word+'乡',cls.STRRET)
        elif cls.street_area_mapper.get(word+'路'):
            return (word+'路',cls.STRRET)
        elif cls.street_area_mapper.get(word+'街'):
            return (word+'街',cls.STRRET)
        elif cls.street_area_mapper.get(word+'办'):
            return (word+'办',cls.STRRET)
        elif cls.city_province_mapper.get(cls.fillCity(word)[0]):
            return (cls.fillCity(word)[0],cls.CITY)
        elif cls.city_province_mapper.get(cls.fillProvince(word)[0]):
            return (cls.fillProvince(word)[0],cls.PROVINCE)
        else:
            return (word,cls.DETAIL)
    
    #如果将“北京市”简写作“北京”，则补全“市”字
    @classmethod
    def fillCity(cls, word):
        if word and not word.endswith("市"):
            return word + "市", True
        return word, False
        
    #如果将“重庆省”简写成“重庆”，则补全“省字”
    @classmethod
    def fillProvince(cls, word):
        if word and not word.endswith("市") and not word.endswith("省"):
            if cls.province_country_mapper.get(word + "市"):
                return word + "市", True
            if cls.province_country_mapper.get(word + "省"):
                return word + "省", True
        return word, False
            
    
        
    
        
