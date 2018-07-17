# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 18:45:10 2018

@author: 燃烧杯
"""
from .infrastructure import SuperMap

#代表一个(省，市，区)组成的地点
class Location:
    
    #直辖市
    #municipality = ["北京市", "天津市", "上海市", "重庆市"] 
    
    def __init__(self):
        self.province = Province()
        self.city = City()
        self.area = Area()
        self.detail=Detail()
        self.street=Street()
    def setPlace(self, name, place_type):
        if not hasattr(self, place_type):
            from .exceptions import PlaceTypeNotExistException
            raise PlaceTypeNotExistException(place_type + \
                                                              " 地区类型不存在")
        if getattr(self, place_type).isEmpty():
            getattr(self, place_type).setPlace(name)
        
    def pca_map(self, umap):
        if self.street.isEmpty():
            if self.area.isEmpty():
                self.__city_and_province()
            else:
                if (self.area.name not in SuperMap.rep_areas) or (umap.get(self.area.name)):
                    if umap.get(self.area.name):
                        tmp = umap.get(self.area.name)
                    else:
                        tmp = SuperMap.area_city_mapper.get(self.area.name)
                    if self.city.isEmpty() or self.city.precision == 0:
                        self.city.setPlace(tmp)
                    elif self.city.isNotEmpty() and self.city.precision == 1:
                        if not self.area.isBlong(self.city.name) \
                            and umap.get(self.area.name) != self.city.name:
                            self.area.reset()
                    self.__city_and_province()
                else:#重复区名 代码执行路径
                    import logging
                    SuperMap.rep_area_set.add(self.area.name)
                    logging.warning("在多个市存在相同区名-'" + self.area.name + \
                                    "'，最好在CPCATransformer的构造函数传入一个map指定其所属市")
                    if self.city.isNotEmpty():
                        self.__city_and_province()
        else:
            if self.area.isEmpty():
                if self.city.isEmpty():
                    if self.province.isEmpty():
                        if SuperMap.street_area_mapper.get(self.street.name):
                            self.area.name=SuperMap.street_area_mapper.get(self.street.name)
                        if SuperMap.area_city_mapper.get(self.area.name):
                            self.city.name=SuperMap.area_city_mapper.get(self.area.name)
                        if SuperMap.city_province_mapper.get(self.city.name):
                            self.province.name=SuperMap.city_province_mapper.get(self.city.name)
                            #print(self.street.name)
                        
                else:
                    self.__city_and_province()
            else:
                if (self.area.name not in SuperMap.rep_areas) or (umap.get(self.area.name)):
                    if umap.get(self.area.name):
                        tmp = umap.get(self.area.name)
                    else:
                        tmp = SuperMap.area_city_mapper.get(self.area.name)
                    if self.city.isEmpty() or self.city.precision == 0:
                        self.city.setPlace(tmp)
                    elif self.city.isNotEmpty() and self.city.precision == 1:
                        if not self.area.isBlong(self.city.name) \
                            and umap.get(self.area.name) != self.city.name:
                            self.area.reset()
                    self.__city_and_province()
                else:#重复区名 代码执行路径
                    import logging
                    SuperMap.rep_area_set.add(self.area.name)
                    logging.warning("在多个市存在相同区名-'" + self.area.name + \
                                    "'，最好在CPCATransformer的构造函数传入一个map指定其所属市")
                    if self.city.isNotEmpty():
                        self.__city_and_province()
           
                        
        if self.city.name.isdigit():
            self.city.reset()
        if not self.province.name:
            self.province.name=''
        if not self.city.name:
            self.city.name=''
        if not self.area.name:
            self.area.name=''
        
        import pandas as pd
        #组装成DataFrame
        return pd.DataFrame({"省":[self.province.name], "市":[self.city.name], \
                             "区":[self.area.name],'街道/乡镇':[self.street.name],'详细地址':[self.detail.name]})
                        
    def __city_and_province(self):
        if self.city.isNotEmpty() and self.province.isNotEmpty():
            if not self.city.isBlong(self.province.name):
                if self.city.precision > self.province.precision:
                    self.province.name = self.city.belong
                else:
                    self.city.reset()
        elif self.city.isNotEmpty() and self.province.isEmpty():
            self.province.name = self.city.belong
        
        
class Place:
    
    def __init__(self, name=""):
        self.name = name
        self.precision = 1


    def reset(self):
        self.name = ""
    
    def isBlong(self, mayBe):
        return self.belong == mayBe
        
    def isEmpty(self):
        return False if self.name else True
    
    def isNotEmpty(self):
        return True if self.name else False
    

class City(Place):
    
    def __init__(self, name=""):
        super().__init__()
        
    def __getBlong(self):
        return SuperMap.city_province_mapper.get(self.name)
        
    def setPlace(self, name):
        self.name, isfilled = SuperMap.fillCity(name)
        if isfilled:#如果是需要补充字的，则认为这个匹配准确率比较低
            self.precision = 0
        self.belong = self.__getBlong()
        
class Province(Place):
    
    def __init__(self, name=""):
        super().__init__()
        
    def __getBlong(self):
        return SuperMap.province_country_mapper.get(self.name)
        
    def setPlace(self, name):
        self.name, isfilled = SuperMap.fillProvince(name)
        if isfilled:#如果是需要补充字的，则认为这个匹配准确率比较低
            self.precision = 0
        self.belong = self.__getBlong()
        
class Area(Place):
    
    def __init__(self, name=""):
        super().__init__()
        
    def __getBlong(self):
        return SuperMap.area_city_mapper.get(self.name)
        
    def setPlace(self, name):
        self.name = name
        self.precision = 1
        self.belong = self.__getBlong()
        
class Detail(Place):
    
    def __init__(self, name=""):
        super().__init__()
        
    def __getBlong(self):
        return SuperMap.area_city_mapper.get(self.name)
        
    def setPlace(self, name):
        self.name = name
        self.precision = 1
        self.belong = self.__getBlong()
class Street(Place):
    
    def __init__(self, name=""):
        super().__init__()
        
    def __getBlong(self):
        return SuperMap.street_area_mapper.get(self.name)
        
    def setPlace(self, name):
        self.name = name
        self.precision = 1
        self.belong = self.__getBlong()
        

    

        
        
 
        
    
        
