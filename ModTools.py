import os
import re
import shutil
import pandas as pd
from types import SimpleNamespace
from lxml import etree
import xml.etree.ElementTree as ET
from xml.dom import minidom
import random 
import sys
import time

# mod一键生成
# 基本参数

# 工程文件路径
path = os.path.expanduser("~/Documents/Firaxis ModBuddy/Civilization VI")
# print(f"工程文件路径: {path}")
# 读取 Excel 文件
file_path = "mod工具 - Mujica.xlsx"  # 文件名
Authors = "Siqi" # 作者

NewCivdata = pd.read_excel(file_path, sheet_name="NewCiv", engine='openpyxl')# 读取 NewCiv sheet
Districtdata = pd.read_excel(file_path, sheet_name="District", engine='openpyxl')# 读取 District sheet
Buildingdata = pd.read_excel(file_path, sheet_name="Building", engine='openpyxl')# 读取 Building sheet
Unitdata = pd.read_excel(file_path, sheet_name="Unit", engine='openpyxl')# 读取 Unit sheet
Improvementdata = pd.read_excel(file_path, sheet_name="Improvement", engine='openpyxl')# 读取 Improvement sheet
Governordata = pd.read_excel(file_path, sheet_name="Governor", engine='openpyxl')# 读取 Governor sheet
Policydata = pd.read_excel(file_path, sheet_name="Policy", engine='openpyxl')# 读取 Policy sheet
Projectdata = pd.read_excel(file_path, sheet_name="Project", engine='openpyxl')# 读取 Project sheet
CityNamedata = pd.read_excel(file_path, sheet_name="CityName", engine='openpyxl')# 读取 CityName sheet
CitizenNamedata = pd.read_excel(file_path, sheet_name="CitizenName", engine='openpyxl')# 读取 CitizenName sheet
DiploTextdata = pd.read_excel(file_path, sheet_name="DiploText", engine='openpyxl')# 读取 DiploText sheet
# 基本工具函数

# 获取数据中第一列符合条件的所有行，并且剔除NaN值
def GetFirstColRows(params, condition):
    rows = []
    for index, row in params.iterrows():
        if row.iloc[0] == condition :
            rows.append(row.dropna().tolist())
    return pd.DataFrame(rows)

DBUI = ['区域', '建筑', '单位', '改良']

# 寻找数据中第二列符合条件的行的第一列元素，只找第一个，并且这个元素必须在DBUI里
def FindFirstColBySecondCol(params, condition):
    for index, row in params.iterrows():
        if row.iloc[1] == condition :
            if row.iloc[0] in DBUI:
                return row.iloc[0]
    return None

# 获取第一列和第二列都符合条件的行，并且剔除NaN值
def GetFirstColBySecondColRows(params, condition1, condition2):
    rows = []
    for index, row in params.iterrows():
        if row.iloc[0] == condition1 and row.iloc[1] == condition2:
            rows.append(row.dropna().tolist())
    return pd.DataFrame(rows)

# 获取第i列符合条件的所有行，并且剔除NaN值
def GetThirdColByIColRows(params, condition, i):
    rows = []
    for index, row in params.iterrows():
        if row.iloc[i] == condition :
            rows.append(row.dropna().tolist())
    return pd.DataFrame(rows)

# 获取数据中第i列的所有行，不剔除NaN值
def GetThirdColRows(params,i):
    rows = []
    for index, row in params.iterrows():
        if not pd.isna(row.iloc[i]):
            rows.append(row.dropna().tolist())
    return pd.DataFrame(rows)

# 获取数据中第一行符合条件的某列元素，并且输出为列表,不剔除NaN值
def get_column_by_header(params, header_name):
    """
    根据第一行的列名查找对应的列数据
    """
     # 遍历所有列（从第0列开始）
    t = params.columns.tolist()
    for col_idx in range(len(params.columns)):
        # 检查第一行的值是否匹配
        if t[col_idx] == header_name:
            # 返回该列从第二行开始的所有数据（保留空值）
            return params.iloc[0:, col_idx].tolist()
    
    return None  # 没有找到对应的列名

# 格式转换函数
def convert_to_format(text):
    return '_'.join(part.capitalize() for part in text.lower().split('_'))

# 转化为,间隔;结尾
def convert_to_comma(List):
    return ','.join(List) + ';'
# 转化为,间隔
def convert_to_comma_noend(List):
    return ','.join(List)
# 转化为,间隔;结尾（换行版）
def convert_to_comma_newline(List):
    return ',\n'.join(List) + ';'
# 转化为,间隔（换行版）
def convert_to_comma_noend_newline(List):
    return ',\n'.join(List)

BaseData = GetFirstColRows(NewCivdata, "基本信息")
# 全局参数
fileName = BaseData.iloc[0, 1]  # mod 名称
Language = BaseData.iloc[0, 2]  # 语言
Prefix = BaseData.iloc[0, 3] + "_"  # 前缀
Midfix = BaseData.iloc[0, 4] # 中缀
SupportFile = BaseData.iloc[0, 5] == 1 # 需要辅助文件（布尔值）
AutoIconString = BaseData.iloc[0, 6] == 1 # 自动生成图标（布尔值）
PediaText = BaseData.iloc[0, 7] == 1 # 需要百科文本
LoadOrderNumber = int(BaseData.iloc[0, 8])  # 加载顺序
StopMain = BaseData.iloc[0, 9] == 1 # 停用主文件（布尔值）

FilePath = path + "\\" + fileName + "\\" + fileName

# 获取各类数据
CivData = GetFirstColRows(NewCivdata, "文明")
LeaderData = GetFirstColRows(NewCivdata, "领袖")
DistrictData = GetFirstColRows(NewCivdata, "区域")
BuildingData = GetFirstColRows(NewCivdata, "建筑")
UnitData = GetFirstColRows(NewCivdata, "单位")
ImprovementData = GetFirstColRows(NewCivdata, "改良")


CivTraitData = GetFirstColRows(NewCivdata, "文明绑定")
LeaderTraitData = GetFirstColRows(NewCivdata, "领袖绑定")
CivTraitGrovernorData = GetFirstColRows(NewCivdata, "总督绑定文明")
LeaderTraitGrovernorData = GetFirstColRows(NewCivdata, "总督绑定领袖")

# 通用SQL语句头
InsertHead = "INSERT INTO "
ValuesHead = " VALUES\n"

# sql表的列名
# 通用列名
TypeRows = ["Type", "Kind"]
TraitRows = ["TraitType", "Name", "Description"]

# 通用前缀
CommonPrefix = {"文明": "CIVILIZATION_", "领袖": "LEADER_", "区域": "DISTRICT_", "建筑": "BUILDING_", "单位": "UNIT_", "改良": "IMPROVEMENT_", "项目": "PROJECT_", "总督": "GOVERNOR_", "政策": "POLICY_"}
# 通用中缀
CommonMidfix = {"文明": "C00", "领袖": "L00", "区域": "D00", "建筑": "B00", "单位": "U00", "改良": "I00", "项目": "P00", "总督": "G00", "政策": "PC00"}

# 文明类
CivilizationsRows = ["CivilizationType", "Name", "Description", "Adjective", "StartingCivilizationLevelType","Ethnicity", "RandomCityNameDepth"]
CivilizationLeadersRows = ["CivilizationType", "LeaderType", "CapitalName"]
CivilizationTraitsRows = ["CivilizationType", "TraitType"]
CityNamesRows = ["CivilizationType", "CityName"]
CivilizationCitizenNamesRows = ["CivilizationType", "CitizenName", "Female", "Modern"]

# 领袖类
LeadersRows = ["LeaderType", "Name","Sex", "InheritFrom", "SceneLayers"]
LeaderQuotesRows = ["LeaderType", "Quote"]
LeaderTraitsRows = ["LeaderType", "TraitType"]
LoadingInfoRows = ["LeaderType", "ForegroundImage", "BackgroundImage", "PlayDawnOfManAudio", "LeaderText"]

# Config类
PlayersRows = ["Domain", "CivilizationType", "CivilizationName", "CivilizationIcon", "CivilizationAbilityName", "CivilizationAbilityDescription", "CivilizationAbilityIcon", "LeaderType", "LeaderName", "LeaderIcon", "LeaderAbilityName", "LeaderAbilityDescription", "LeaderAbilityIcon", "Portrait", "PortraitBackground"]
PlayerItemsRows = ["Domain", "CivilizationType", "LeaderType", "Type", "Icon", "Name", "Description", "SortIndex"]

# Icons类
IconTextureAtlasesRows = ['Name', 'IconSize', 'Filename']
IconDefinitionsRows = ['Name', 'Atlas', 'Index']
IconAliasesRows = ['Name', 'OtherName']

CivilizationSize = [22, 30, 32, 36, 44, 45, 48, 50, 64, 80, 128, 200, 256]
LeaderSize = [32, 45, 48, 50, 55, 64, 80, 256]
DistrictSize = [22, 32, 38, 50, 80, 128, 256]
BuildingSize = [32, 38, 50, 80, 128, 256]
UnitSize = [22, 32, 38, 50, 80, 128, 256]
UnitPortraitSize = [38, 50, 70, 95, 200, 256]
ImprovementSize = [38, 50, 80, 256]
ProjectSize = [30, 32, 38, 50, 70, 80, 256]
GovernorSize = [22, 32]
GovernorSize2 = [22, 32, 64]

# 区域类
DistrictReplacesRows = ['CivUniqueDistrictType','ReplacesDistrictType']
DistrictsRows = ['DistrictType','Name','Description','TraitType','PrereqTech','PrereqCivic', 'Coast', 'Cost','RequiresPlacement','RequiresPopulation','NoAdjacentCity','CityCenter','Aqueduct','InternalOnly','ZOC','FreeEmbark','HitPoints','CaptureRemovesBuildings','CaptureRemovesCityDefenses','PlunderType','PlunderAmount','TradeEmbark','MilitaryDomain','CostProgressionModel','CostProgressionParam1','Appeal','Housing','Entertainment','OnePerCity','AllowsHolyCity','Maintenance','AirSlots','CitizenSlots','TravelTime','CityStrengthModifier','AdjacentToLand','CanAttack','AdvisorType','CaptureRemovesDistrict','MaxPerPlayer']
Districts_XP2Rows = ['DistrictType','OnePerRiver','PreventsFloods','PreventsDrought','Canal','AttackRange']
District_TradeRouteYieldsRows = ['DistrictType','YieldType','YieldChangeAsOrigin','YieldChangeAsDomesticDestination','YieldChangeAsInternationalDestination']
District_GreatPersonPointsRows = ['DistrictType','GreatPersonClassType','PointsPerTurn']
District_CitizenYieldChangesRows = ['DistrictType','YieldType','YieldChange']
District_AdjacenciesRows = ['DistrictType','YieldChangeId']

# 建筑类
BuildingReplacesRows = ['CivUniqueBuildingType','ReplacesBuildingType']
BuildingsRows = ['BuildingType','Name','Description','TraitType','PrereqTech','PrereqCivic','Cost','MaxPlayerInstances','MaxWorldInstances','Capital','PrereqDistrict','AdjacentDistrict','RequiresPlacement','RequiresRiver','OuterDefenseHitPoints','Housing','Entertainment','AdjacentResource','Coast','EnabledByReligion','AllowsHolyCity','PurchaseYield','MustPurchase','Maintenance','OuterDefenseStrength','CitizenSlots','MustBeLake','MustNotBeLake','RegionalRange','AdjacentToMountain','ObsoleteEra','RequiresReligion','GrantFortification','DefenseModifier','RequiresAdjacentRiver','MustBeAdjacentLand','AdvisorType','AdjacentCapital','AdjacentImprovement','CityAdjacentTerrain','UnlocksGovernmentPolicy','GovernmentTierRequirement']
BuildingPrereqsRows = ['Building','PrereqBuilding']
BuildingYieldChangesRows = ['BuildingType','YieldChange','YieldType']
BuildingGreatPersonPointsRows = ['BuildingType','PointsPerTurn','GreatPersonClassType']
BuildingXP2Rows = ['BuildingType','RequiredPower','ResourceTypeConvertedToPower','PreventsFloods','PreventsDrought','BlocksCoastalFlooding','CostMultiplierPerTile','CostMultiplierPerSeaLevel','Bridge','CanalWonder','EntertainmentBonusWithPower','NuclearReactor','Pillage']
BuildingYieldChangesBonusWithPowerRows = ['BuildingType','YieldType','YieldChange']
BuildingCitizenYieldChangesRows = ['BuildingType','YieldType','YieldChange']
BuildingTourismBombs_XP2Rows = ['BuildingType','TourismBombValue']
Building_YieldDistrictCopiesRows = ['BuildingType','OldYieldType','NewYieldType']
Building_YieldsPerEraRows = ['BuildingType','YieldType','YieldChange']

# 单位类
UnitAiInfosRows = ['UnitType','AiType']
TagsRows = ['Tag', 'Vocabulary']
TypeTagsRows = ['Type','Tag']
UnitReplacesRows = ['CivUniqueUnitType','ReplacesUnitType']
UnitsRows = ['UnitType','Name','Description','TraitType','BaseSightRange','BaseMoves','Combat','RangedCombat','Range','Bombard','Domain','FormationClass','Cost','PopulationCost','FoundCity','FoundReligion','MakeTradeRoute','EvangelizeBelief','LaunchInquisition','RequiresInquisition','BuildCharges','ReligiousStrength','ReligionEvictPercent','SpreadCharges','ReligiousHealCharges','ExtractsArtifacts','Flavor','CanCapture','CanRetreatWhenCaptured','AllowBarbarians','CostProgressionModel','CostProgressionParam1','PromotionClass','InitialLevel','NumRandomChoices','PrereqTech','PrereqCivic','PrereqDistrict','PrereqPopulation','LeaderType','CanTrain','StrategicResource','PurchaseYield','MustPurchase','Maintenance','Stackable','AirSlots','CanTargetAir','PseudoYieldType','ZoneOfControl','AntiAirCombat','Spy','WMDCapable','ParkCharges','IgnoreMoves','TeamVisibility','ObsoleteTech','ObsoleteCivic','MandatoryObsoleteTech','MandatoryObsoleteCivic','AdvisorType','EnabledByReligion','TrackReligion','DisasterCharges','UseMaxMeleeTrainedStrength','ImmediatelyName','CanEarnExperience']
UnitsXP2Rows = ['UnitType','ResourceMaintenanceAmount','ResourceCost','ResourceMaintenanceType','TourismBomb','CanEarnExperience','TourismBombPossible','CanFormMilitaryFormation','MajorCivOnly','CanCauseDisasters','CanSacrificeUnits']
UnitUpgradesRows = ['Unit','UpgradeUnit']
Units_MODERows = ['UnitType','ActionCharges']
UnitCapturesRows = ['CapturedUnitType','BecomesUnitType']

# 改良类 
ImprovementsRows = ['ImprovementType','Name','Description','TraitType','Icon','PrereqTech','PrereqCivic','Buildable','RemoveOnEntry','DispersalGold','PlunderType','PlunderAmount','Goody','TilesPerGoody','GoodyRange','Housing','TilesRequired','SameAdjacentValid','RequiresRiver','EnforceTerrain','BuildInLine','CanBuildOutsideTerritory','BuildOnFrontier','AirSlots','DefenseModifier','GrantFortification','MinimumAppeal','Coast','YieldFromAppeal','WeaponSlots','ReligiousUnitHealRate','Appeal','OnePerCity','YieldFromAppealPercent','ValidAdjacentTerrainAmount','Domain','AdjacentSeaResource','RequiresAdjacentBonusOrLuxury','MovementChange','Workable','ImprovementOnRemove','GoodyNotify','NoAdjacentSpecialtyDistrict','RequiresAdjacentLuxury','AdjacentToLand','Removable','OnlyOpenBorders','Capturable']
Improvements_XP2Rows = ['ImprovementType','AllowImpassableMovement','BuildOnAdjacentPlot','PreventsDrought','DisasterResistant']
Improvement_ValidBuildUnitsRows = ['ImprovementType','UnitType']
Improvement_YieldChangesRows = ['ImprovementType','YieldType','YieldChange']
Improvement_ValidTerrainsRows = ['ImprovementType','TerrainType']
Improvement_ValidFeaturesRows = ['ImprovementType','FeatureType']
Improvement_TourismsRows = ['ImprovementType','TourismSource','PrereqTech','PrereqCivic','ScalingFactor']

# 总督类
GovernorsRows = ['GovernorType','Name','Description','TraitType','Title','ShortTitle','Image','PortraitImage','PortraitImageSelected','IdentityPressure','TransitionStrength','AssignCityState']
Governors_XP2Rows = ['GovernorType','AssignToMajor']
GovernorPromotionSetsRows = ['GovernorType','GovernorPromotion']
GovernorPromotionsRows = ['GovernorPromotionType','Name','Description','Level','Column','BaseAbility']
GovernorPromotionPrereqsRows = ['GovernorPromotionType','PrereqGovernorPromotion']

# 项目类
ProjectsRows = ['ProjectType','Name','ShortName','Description','PopupText','Cost','CostProgressionModel','CostProgressionParam1','PrereqTech','PrereqCivic','PrereqDistrict','RequiredBuilding','VisualBuildingType','SpaceRace','OuterDefenseRepair','MaxPlayerInstances','AmenitiesWhileActive','PrereqResource','AdvisorType','WMD','UnlocksFromEffect']
Projects_XP1Rows = ['ProjectType','IdentityPerCitizenChange']
Projects_XP2Rows = ['ProjectType','RequiredPowerWhileActive','ReligiousPressureModifier','RequiredBuilding','CreateBuilding','FullyPoweredWhileActive','MaxSimultaneousInstances']
Projects_MODERows = ['ProjectType','PrereqImprovement','ResourceType']
Project_BuildingCostsRows = ['ProjectType','ConsumedBuildingType']
Project_GreatPersonPointsRows = ['ProjectType','GreatPersonClassType','Points','PointProgressionModel','PointProgressionParam1']
Project_ResourceCostsRows = ['ProjectType','ResourceType','StartProductionCost']
Project_YieldConversionsRows = ['ProjectType','YieldType','PercentOfProductionRate']

# 政策类
PoliciesRows = ['PolicyType','Name','Description','PrereqCivic','PrereqTech','GovernmentSlotType','RequiresGovernmentUnlock','ExplicitUnlock']
Policies_XP1Rows = ['PolicyType','MinimumGameEra','MaximumGameEra','RequiresDarkAge','RequiresGoldenAge']
Policy_GovernmentExclusives_XP2Rows = ['PolicyType','GovernmentType']

# 其他类
# 历史时刻
MomentIllustrationsRows = ['MomentIllustrationType', 'MomentDataType', 'GameDataType', 'Texture']
def MomentTypes(Type, String):
    if Type == "DISTRICT":
        return  f"('MOMENT_ILLUSTRATION_UNIQUE_DISTRICT', 'MOMENT_DATA_DISTRICT', '{String}', 'Moment_UniqueDistrict_{convert_to_format(String.replace('DISTRICT_', ''))}.png')"
    elif Type == "BUILDING":
        return  f"('MOMENT_ILLUSTRATION_UNIQUE_BUILDING', 'MOMENT_DATA_BUILDING', '{String}', 'Moment_UniqueBuilding_{convert_to_format(String.replace('BUILDING_', ''))}.png')"
    elif Type == "UNIT":
        return  f"('MOMENT_ILLUSTRATION_UNIQUE_UNIT', 'MOMENT_DATA_UNIT', '{String}', 'Moment_UniqueUnit_{convert_to_format(String.replace('UNIT_', ''))}.png')"
    elif Type == "IMPROVEMENT":
        return  f"('MOMENT_ILLUSTRATION_UNIQUE_IMPROVEMENT', 'MOMENT_DATA_IMPROVEMENT', '{String}', 'Moment_UniqueImprovement_{convert_to_format(String.replace('IMPROVEMENT_', ''))}.png')"
    elif Type == "GOVERNOR":
        return  f"('MOMENT_ILLUSTRATION_GOVERNOR', 'MOMENT_DATA_GOVERNOR', '{String}', 'Moment_UniqueGovernor_{convert_to_format(String.replace('GOVERNOR_', ''))}.png')"
    
#UI类
UIXml = '<?xml version="1.0" encoding="utf-8"?>\n<Context></Context>'

#文本类
LocalizedText = 'INSERT INTO LocalizedText (Language, Tag, Text) VALUES'
CN = 'zh_Hans_CN'
EN = 'en_US'
HK = 'zh_Hant_HK'
# 将换行符替换为[NEWLINE]
def RN(text):
    return str(text).replace('\n', '[NEWLINE]')

# 伟人类
GREATPERSON = ["GREAT_PERSON_CLASS_SCIENTIST", "GREAT_PERSON_CLASS_GENERAL", "GREAT_PERSON_CLASS_ENGINEER", "GREAT_PERSON_CLASS_MERCHANT", "GREAT_PERSON_CLASS_ADMIRAL", "GREAT_PERSON_CLASS_PROPHET", "GREAT_PERSON_CLASS_WRITER", "GREAT_PERSON_CLASS_ARTIST", "GREAT_PERSON_CLASS_MUSICIAN"]

# 产出类
YIELDTYPE = ["YIELD_GOLD", "YIELD_FOOD", "YIELD_PRODUCTION", "YIELD_SCIENCE", "YIELD_CULTURE", "YIELD_FAITH"]

# 地形类
TERRAINTYPE = ['TERRAIN_GRASS','TERRAIN_GRASS_HILLS','TERRAIN_GRASS_MOUNTAIN','TERRAIN_PLAINS','TERRAIN_PLAINS_HILLS','TERRAIN_PLAINS_MOUNTAIN','TERRAIN_DESERT','TERRAIN_DESERT_HILLS','TERRAIN_DESERT_MOUNTAIN','TERRAIN_TUNDRA','TERRAIN_TUNDRA_HILLS','TERRAIN_TUNDRA_MOUNTAIN','TERRAIN_SNOW','TERRAIN_SNOW_HILLS','TERRAIN_SNOW_MOUNTAIN','TERRAIN_COAST','TERRAIN_OCEAN']

# 地貌类
FEATURETYPE = ['FEATURE_FLOODPLAINS','FEATURE_JUNGLE','FEATURE_FOREST','FEATURE_OASIS','FEATURE_MARSH','FEATURE_REEF','FEATURE_FLOODPLAINS_GRASSLAND','FEATURE_FLOODPLAINS_PLAINS','FEATURE_GEOTHERMAL_FISSURE','FEATURE_VOLCANO','FEATURE_VOLCANIC_SOIL']


# xml基础函数

# xml头
def xml(str):
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<GameData>\n{str}\n</GameData>'

# xml标签
def xmltab(str, tab):
    return f'<{tab}>\n{str}\n</{tab}>'

# xml行标签
def xmlitem(str):
    return f'<Row {str} />'

# 格式化 XML
def format_xml(xml_string):
    parser = etree.XMLParser(remove_blank_text=True)
    xml_bytes = xml_string.encode('utf-8')
    root = etree.fromstring(xml_bytes, parser)
    
    # 获取格式化后的 XML
    formatted = etree.tostring(
        root, 
        pretty_print=True, 
        encoding='utf-8', 
        xml_declaration=True
    ).decode('utf-8')
    
    return formatted

# 将字符串插入到某个<></>的标签中
def insert_into_tag(xml_string, tag, content):
    pattern = re.compile(rf'(<{tag}.*?>)(.*?)(</{tag}>)', re.DOTALL)
    match = pattern.search(xml_string)
    if match:
        start_tag, inner_content, end_tag = match.groups()
        new_inner_content = inner_content + content
        new_xml_string = pattern.sub(f'{start_tag}{new_inner_content}{end_tag}', xml_string)
        return new_xml_string
    else:
        raise ValueError(f"Tag <{tag}> not found in the provided XML string.")

# sql基础函数

# 将列表转换为 SQL 语句中的元组字符串,如果是NULL或数字就不加''
def ListToSQLTuple(lst):
    new_lst = []
    for item in lst:
        if isinstance(item, (int, float)):  # 如果是数字类型
            new_lst.append(str(item))  # 直接转换为字符串
        elif item == "NULL":
            new_lst.append(item)  # 直接添加NULL
        else:
            new_lst.append(f"'{item}'")  # 否则加上引号
    return "(" + ", ".join(new_lst) + ")"

# 将列表转换为 SQL 语句中的元组字符串(换行版)
def ListToSQLTupleNewLine(lst):
    new_lst = []
    for item in lst:
        if isinstance(item, (int, float)):  # 如果是数字类型
            new_lst.append(str(item))  # 直接转换为字符串
        elif item == "NULL":
            new_lst.append(item)  # 直接添加NULL
        else:
            new_lst.append(f"'{item}'")  # 否则加上引号
    return "(\n  " + ",\n  ".join(new_lst) + "\n)"

# 将列表转换为 SQL 语句中的元组字符串(无引号版)
def ListToSQLTupleNoQuote(lst):
    return "(" + ",".join(lst) + ")"

# 将列表转换为 SQL 语句中的元组字符串(无引号版换行版)
def ListToSQLTupleNoQuoteNewLine(lst):
    return "(\n  " + ",\n  ".join(lst) + "\n)"

# 文本特供将表转化为 SQL 语句中的元组字符串
def ListToSQLTupleText(Lang, Tag, Text):
    return "('" + Lang + "','" + Tag + "','" + Text + "'),"

# 将列表转换为 SQL 的SELECT语句 
def ListToSQLSelect(lst):
    return "SELECT " + ", ".join(lst)

# 将列表转换为 SQL 的SELECT语句(换行版) #如果是NULL或数字，就不加引号
def ListToSQLSelectNewLine(lst):
    return "SELECT \n  " + ",\n  ".join(lst) + "\n"

# SELECT语句辅助函数
def SQLSelectHelper(string, From, Where, Type):
    return f"SELECT '{string}' FROM {From} WHERE {Where} = '{Type}'"

# 让字符串两边加单引号
def SQLString(string):
    return f"'{string}'"

# 基于表名给出Values语句
def SQLValues(tableName, Rows):
    return f"{InsertHead} {tableName} "+ ListToSQLTupleNoQuote(Rows) + ValuesHead

# 基于表名给出SELECT语句
def SQLSelect(tableName, Rows):
    return f"{InsertHead} {tableName} "+ ListToSQLTupleNoQuote(Rows)

# 基于表名给出Values语句(换行版)
def SQLValuesNewLine(tableName, Rows):
    return f"{InsertHead} {tableName} "+ ListToSQLTupleNoQuoteNewLine(Rows) + "\n" + ValuesHead

# 基于表名给出SELECT语句(换行版)
def SQLSelectNewLine(tableName, Rows):
    return f"{InsertHead} {tableName} "+ ListToSQLTupleNoQuoteNewLine(Rows) + "\n"

# 工具函数
# 获取中缀
def GetMidfix(Kind):
    if Midfix != 0:
        return f"{CommonMidfix[Kind]}{Midfix}_"
    else:
        return ""

# 获得Name和Description
def GetNameDescription(string):
    return 'LOC_' + string + '_NAME', 'LOC_' + string + '_DESCRIPTION'

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# Type表和Trait表
TypeHead = SQLValues("Types", TypeRows)
TraitHead = SQLValues("Traits", TraitRows)

# 构建 SQL 语句的Type表， 输出SQL语句字符串
def GetTypeRows(params, Kind, HasTrait):
    rows = []
    for row in params:
        rows.append(ListToSQLTuple([row, Kind]))
    if HasTrait:
        for row in params:
            rows.append(ListToSQLTuple(['TRAIT_' + row, 'KIND_TRAIT'])) 
            
    return TypeHead + convert_to_comma_newline(rows)

# 获得Trait表
def GetTraitRows(params):
    rows = []
    for row in params:
        rows.append(ListToSQLTuple(['TRAIT_' + row, *GetNameDescription('TRAIT_' + row)]))
    return TraitHead + convert_to_comma_newline(rows)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 文明
class Civ:
    def __init__(self, params): # params 是 DataFrame 的一行
        self.ShortType = str(params.iloc[1])
        self.Type = CommonPrefix["文明"] + Prefix + GetMidfix("文明") + self.ShortType
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Adjective = 'LOC_' + self.Type + '_ADJECTIVE'
        self.StartingCivilizationLevelType = 'CIVILIZATION_LEVEL_FULL_CIV'
        self.Ethnicity = 'ETHNICITY_ASIAN'
        self.RandomCityNameDepth = 10
        self.Traits = []
        self.Leaders = []
        self.CityNames = []
        self.City = params.iloc[2]
        self.CityIsValues = False
        self.CitizenNames = []
        self.Citizen = [params.iloc[3], params.iloc[4], params.iloc[5], params.iloc[6]]
        self.CitizenIsValues = False
        self.AddTrait()
        self.AddLeader()
        self.AddCityName()
        self.AddCitizenName()
        self.NameText = RN(params.iloc[7])
        self.AbilityNameText = RN(params.iloc[8])
        self.AbilityDescriptionText = RN(params.iloc[9])
        self.Icon = 'ICON_' + self.Type
        self.Pedia = []
    def GetCivilizationRows(self):
        return ListToSQLTuple([self.Type, self.Name, self.Description, self.Adjective, self.StartingCivilizationLevelType, self.Ethnicity, str(self.RandomCityNameDepth)])
    def GetCivilizationTraitRows(self):
        rows = []
        for trait in self.Traits:
            rows.append(ListToSQLTuple([self.Type, 'TRAIT_' + trait]))
        if len(rows) == 0:
            return ''
        return convert_to_comma_noend_newline(rows)
    def GetCivilizationLeaderRows(self):
        rows = []
        for leader in self.Leaders:
            rows.append(ListToSQLTuple([self.Type, leader, 'LOC_' + leader + '_CAPITAL_NAME']))
        return convert_to_comma_noend_newline(rows)
    def GetCityNameRows(self):
        if self.City == 0:
            return ''
        rows = []
        # 看看是不是大于0的数字
        if isinstance(self.City, int) and self.City > 0:
            # 那就循环城市数量的名字
            i = 1
            for name in self.CityNames:
                rows.append(ListToSQLTuple([self.Type, 'LOC_CITY_NAME_' + Prefix + GetMidfix("文明") + self.ShortType + '_' + str(i)]))
                i += 1
            return convert_to_comma_noend_newline(rows)
        elif self.City == "Self": # 如果是Self，那就是报错
            print("虽然城市名字是Self，但是没有输入城市名字")
            sys.exit(1)
        else: # 那就是复制其他文明的城市名字，使用SELCET语句
            return (f"SELECT '{self.Type}', CityName FROM CityNames WHERE CivilizationType = '{self.City}'")
    def GetCitizenNameRows(self):
        if self.Citizen[0] != 'Self' or (not isinstance(self.Citizen[0], (int, float))):
            return ''
        if sum(self.Citizen) == 0:
            return ''
        rows = []
        if sum(self.Citizen) > 0: # 看看是不是总和大于0的数字
            # 那就循环市民数量的名字
            i = 1
            for name in self.CitizenNames:
                rows.append(ListToSQLTuple([self.Type, 'LOC_CITIZEN_NAME_' + Prefix + GetMidfix("文明") + self.ShortType + '_' + str(i), name[1], name[2]]))
                i += 1
            return convert_to_comma_noend_newline(rows)
        elif "Self" in self.Citizen: # 如果是Self，那就是报错
            sys.exit(1)
        else: # 那就是复制其他文明的市民名字，使用SELCET语句
            return (f"SELECT '{self.Type}', CitizenName, Female, Modern FROM CivilizationCitizenNames WHERE CivilizationType = '{self.Citizen}'")
    def AddTrait(self):# 在CivTraitData里寻找
        # 先把自己的Trait加进去
        self.Traits.append(self.Type)
        for index, row in CivTraitData.iterrows():
            if row.iloc[1] == self.ShortType:
                # 从第3列开始的非NaN值
                for trait in row.dropna().tolist()[2:]:
                    localType = FindFirstColBySecondCol(NewCivdata, trait)
                    if CommonPrefix.get(localType):
                        self.Traits.append(CommonPrefix[localType] + Prefix + GetMidfix(localType) + trait)
    def AddLeader(self):# 在LeaderData里寻找，第二列是领袖简称，第三列是文明简称
        for index, row in LeaderData.iterrows():
            if row.iloc[2] == self.ShortType:
                self.Leaders.append(CommonPrefix["领袖"] + Prefix + GetMidfix("领袖") + row.iloc[1])
    def AddCityName(self):# 在CityNamedata里寻找?
        if not (isinstance(self.City, int) or self.City == "Self"):
            return
        # 看看是不是0
        if self.City == 0:
            return
        # 看看是不是Self
        elif self.City == "Self":
            cities = GetFirstColBySecondColRows(NewCivdata, "文明城市", self.ShortType)
            # 从第3列开始的非NaN值
            i = 0 # 计算城市数量
            for index, row in cities.iterrows():
                for name in row.dropna().tolist()[2:]:#这些都是中文
                    self.CityNames.append(name)
                    i += 1
            if i == 0:
                raise ValueError("虽然城市名字是Self，但是没有输入城市名字")
            self.City = i
            self.CityIsValues = True
        # 看看是不是大于0的数字
        elif isinstance(self.City, int) and self.City > 0:
            # 从CityNamedata抽取符合行数的数据，城市名字在第二列，这是公用城市库，没有文明属性，只有序号，从第二行开始
            # 直接在第二行到第最后一个非NaN值随机抽取self.City个名字
            names = CityNamedata.iloc[1:, 1].dropna().tolist()
            RandNames = random.sample(names, self.City)
            for name in RandNames:
                self.CityNames.append(name)
            self.CityIsValues = True
        else: 
            raise ValueError("城市名字输入错误")
    def AddCitizenName(self):# 在CitizenNamedata里寻找?
        # 看看self.Citize[0]是不是数字（浮点数），只看第一个元素是不是数字
        if (self.Citizen[0] != 'Self') or (not isinstance(self.Citizen[0], (int, float))):
            return
        # 看看总和是不是0
        if sum(self.Citizen) == 0:
            return
        # 看看是不是Self（只要有一个是Self就行）
        elif "Self" in self.Citizen:
            citizens = GetFirstColBySecondColRows(NewCivdata, "文明市民", self.ShortType)
            # 从第5列开始的非NaN值，第3列是性别，第4列是时代
            i = 0 # 计算市民数量
            for index, row in citizens.iterrows():
                for name in row.dropna().tolist()[3:]:#这些都是中文
                    self.CitizenNames.append([name, row.iloc[2], row.iloc[3]])
                    i += 1
            if i == 0:
                raise ValueError("虽然市民名字是Self，但是没有输入市民名字")
            self.Citizen[self.Citizen.index("Self")] = i
            self.CitizenIsValues = True
        # 看看是不是总和大于0的数字
        elif sum(self.Citizen) > 0:
            # 从CitizenNamedata抽取符合行数的数据，市民名字在第二列，这是公用市民库，没有文明属性，没有时代，性别在第4列
            # 直接在第二行到第最后一个非NaN值随机抽取self.Citizen[j]个名字，需要看性别
            MaleNames = GetThirdColByIColRows(CitizenNamedata, 1, 3).iloc[:, 1].dropna().tolist() # 男性名字
            FemaleNames = GetThirdColByIColRows(CitizenNamedata, 0, 3).iloc[:, 1].dropna().tolist() # 女性名字
            RandMaleNames = random.sample(MaleNames, self.Citizen[0] + self.Citizen[1]) # 现代和非现代男性名字
            RandFemaleNames = random.sample(FemaleNames, self.Citizen[2] + self.Citizen[3]) # 现代和非现代女性名字
            for j in range(self.Citizen[0]): # 非现代男性名字
                self.CitizenNames.append([RandMaleNames[j], 0, 0])
            for j in range(self.Citizen[0], self.Citizen[0] + self.Citizen[1]): # 现代男性名字
                self.CitizenNames.append([RandMaleNames[j], 0, 1])
            for j in range(self.Citizen[2]): # 非现代女性名字
                self.CitizenNames.append([RandFemaleNames[j], 1, 0])
            for j in range(self.Citizen[2], self.Citizen[2] + self.Citizen[3]): # 现代女性名字
                self.CitizenNames.append([RandFemaleNames[j], 1, 1])
            self.CitizenIsValues = True
        else: #报错
            raise ValueError("市民名字输入错误")
    def GetPlayerRows(self):
        Rows = []
        for Leader in self.Leaders:
            Row = []
            Row.append('Players:Expansion2_Players')
            Row.append(self.Type)
            Row.append(self.Name)
            Row.append('ICON_' + self.Type)
            Row.append('LOC_TRAIT_' + self.Type + '_NAME')
            Row.append('LOC_TRAIT_' + self.Type + '_DESCRIPTION')
            Row.append('ICON_' + self.Type)
            Row.append(Leader)
            Row.append('LOC_' + Leader + '_NAME')
            Row.append('ICON_' + Leader)
            Row.append('LOC_TRAIT_' + Leader + '_NAME')
            Row.append('LOC_TRAIT_' + Leader + '_DESCRIPTION')
            Row.append('ICON_' + Leader)
            Row.append('PORTRAIT_' + Leader)
            Row.append('PORTRAIT_BACKGROUND_' + Leader)
            Rows.append('-- ' + self.ShortType + ': ' + Leader)
            Rows.append(ListToSQLTupleNewLine(Row))
        return convert_to_comma_noend_newline(Rows)
    def GetPlayerItemRows(self):
        Rows = []
        def Support(LeaderType, trait, Index):
            row = []
            row.append('Players:Expansion2_Players')
            row.append(self.Type)
            row.append(LeaderType)
            row.append(trait)
            row.append('ICON_' + trait)
            row.append('LOC_' + trait + '_NAME')
            row.append('LOC_' + trait + '_DESCRIPTION')
            row.append(Index)
            return ListToSQLTuple(row)
        for leader in self.Leaders:
            i = 10 # 序号
            eLeader = GetFirstColBySecondColRows(LeaderData, "领袖", leader.replace(CommonPrefix["领袖"] + Prefix + GetMidfix("领袖"), ""))
            if eLeader.empty:
                raise ValueError(f"在文明 {self.ShortType} 中，领袖 {leader} 未在数据表中找到")
            pLeader = Leader(eLeader.iloc[0]) # 这里每个领袖简称都是唯一的，获取第一行就行
            # 文明特色
            for trait in self.Traits:
                if trait == self.Type:
                    continue
                Rows.append(Support(leader, trait, i))
                i += 10
            # 领袖特色
            for trait in pLeader.Traits:
                if trait == pLeader.Type:
                    continue
                Rows.append(Support(leader, trait, i))
                i += 10
        return convert_to_comma_noend_newline(Rows)

class Civs:
    def __init__(self, params): # params 是 DataFrame
        self.Civs = []
        for index, row in params.iterrows():
            self.Civs.append(Civ(row))
    def GetTypes(self):
        Types = []
        for civ in self.Civs:
            if civ.Type not in Types:
                Types.append(civ.Type)
        return GetTypeRows(Types, "KIND_CIVILIZATION", True)
    def GetTraits(self):
        Types = []
        for civ in self.Civs:
            if civ.Type not in Types:
                Types.append(civ.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetCivilization(self):
        rows = []
        for civ in self.Civs:
            if civ.GetCivilizationRows() != '':
                rows.append(civ.GetCivilizationRows())
        return SQLValues("Civilizations", CivilizationsRows) + convert_to_comma_newline(rows)
    def GetCityName(self):
        ValuesRows = []
        SelectRows = []
        for civ in self.Civs:
            if civ.CityIsValues and civ.GetCityNameRows() != '':
                ValuesRows.append(civ.GetCityNameRows())
            elif not civ.CityIsValues and civ.GetCityNameRows() != '':
                SelectRows.append(civ.GetCityNameRows())
        ValuesSQL = ''
        SelectSQL = ''
        if len(ValuesRows) > 0:
            ValuesSQL = SQLValues("CityNames", CityNamesRows) + convert_to_comma_newline(ValuesRows)
        if len(SelectRows) > 0:
            SelectSQL = SQLSelect("CityNames", CityNamesRows) + convert_to_comma_newline(SelectRows)
        return ValuesSQL + '\n' + SelectSQL
    def GetCitizenName(self):
        ValuesRows = []
        SelectRows = []
        for civ in self.Civs:
            if civ.CitizenIsValues and civ.GetCitizenNameRows() != '':
                ValuesRows.append(civ.GetCitizenNameRows())
            elif not civ.CitizenIsValues and civ.GetCitizenNameRows() != '':
                SelectRows.append(civ.GetCitizenNameRows())
        ValuesSQL = ''
        SelectSQL = ''
        if len(ValuesRows) > 0:
            ValuesSQL = SQLValues("CivilizationCitizenNames", CivilizationCitizenNamesRows) + convert_to_comma_newline(ValuesRows)
        if len(SelectRows) > 0:
            SelectSQL = SQLSelect("CivilizationCitizenNames", CivilizationCitizenNamesRows) + convert_to_comma_newline(SelectRows)
        return ValuesSQL + '\n' + SelectSQL
    def GetCivilizationLeaders(self):
        rows = []
        for civ in self.Civs:
            rows.append(civ.GetCivilizationLeaderRows())
        return SQLValues("CivilizationLeaders", CivilizationLeadersRows) + convert_to_comma_newline(rows)
    def GetCivilizationTraits(self):
        rows = []
        for civ in self.Civs:
            rows.append(civ.GetCivilizationTraitRows())
        return SQLValues("CivilizationTraits", CivilizationTraitsRows) + convert_to_comma_newline(rows)
    def GetPlayerRows(self):
        Rows = []
        for civ in self.Civs:
            Rows.append(civ.GetPlayerRows())
        return SQLValuesNewLine("Players", PlayersRows) + convert_to_comma_newline(Rows)
    def GetPlayerItemRows(self):
        Rows = []
        for civ in self.Civs:
            Rows.append(civ.GetPlayerItemRows())
        return SQLValues("PlayerItems", PlayerItemsRows) + convert_to_comma_newline(Rows)
    
# 文明文件主函数:
def CivMain():
    if len(CivData) == 0:
        return
    CivsData = Civs(CivData)
    CivSQL = []
    CivSQL.append('-- Types and Traits')
    CivSQL.append(CivsData.GetTypes())
    CivSQL.append(CivsData.GetTraits())
    CivSQL.append('-- Civilizations')
    CivSQL.append(CivsData.GetCivilization())
    CivSQL.append('-- Civilization Traits')
    CivSQL.append(CivsData.GetCivilizationTraits())
    CivSQL.append('-- Civilization Leaders')
    CivSQL.append(CivsData.GetCivilizationLeaders())
    CivSQL.append('-- City Names')
    CivSQL.append(CivsData.GetCityName())
    CivSQL.append('-- Citizen Names')
    CivSQL.append(CivsData.GetCitizenName())
    CivSQLStr = '\n\n'.join(CivSQL)
    CivilizationFile = FilePath + "\\" + fileName + "_Civilizations.sql"
    with open(CivilizationFile, "w", encoding="utf-8") as f:
        f.write(CivSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 领袖
class Leader:
    def __init__(self, params): # params 是 DataFrame 的一行
        self.ShortType = str(params.iloc[1])
        self.Type = CommonPrefix["领袖"] + Prefix + GetMidfix("领袖") + self.ShortType
        self.Name, self.Description = GetNameDescription(self.Type)
        self.IsFemale = params.iloc[3] == 0
        self.CapitalName = params.iloc[4]
        self.Traits = []
        self.NameText = RN(params.iloc[7])
        self.AbilityNameText = RN(params.iloc[8])
        self.AbilityDescriptionText = RN(params.iloc[9])
        self.LoadingText = RN(params.iloc[10])
        self.QuoteText = RN(params.iloc[11])
        self.Pedia = []
        self.AddTrait()
    def GetLeaderRows(self):
        F = 'Male' if not self.IsFemale else 'Female'
        return ListToSQLTuple([self.Type, self.Name, F, 'LEADER_DEFAULT', 4])
    def GetLeaderQuotesRows(self):
        return ListToSQLTuple([self.Type, 'LOC_PEDIA_LEADERS_PAGE_' + Prefix + GetMidfix("领袖") + self.ShortType + '_QUOTE'])
    def GetLeaderTraitRows(self):
        rows = []
        for trait in self.Traits:
            rows.append(ListToSQLTuple([self.Type, 'TRAIT_' + trait]))
        if len(rows) == 0:
            return ''
        return convert_to_comma_noend_newline(rows)
    def GetLoadingInfoRows(self):
        Rows = []
        Rows.append(self.Type)
        Rows.append(self.Type + '_NEUTRAL')
        Rows.append(self.Type + '_BACKGROUND')
        Rows.append(1) # PlayDawnOfManAudio
        Rows.append('LOC_LOADING_INFO_' + self.Type)
        return ListToSQLTuple(Rows)
    def GetDiplomacyImage(self):
        Lead = Prefix + GetMidfix("领袖") + self.ShortType
        ImpForegroundImage = 'FALLBACK_NEUTRAL_' + Lead
        ImpBackgroundImage1 = Lead + '_1'
        ImpBackgroundImage2 = Lead + '_2'
        ImpBackgroundImage3 = Lead + '_3'
        Name = "领袖" + self.NameText
        return "--" + Name + "外交肖像：" + ImpForegroundImage + "\n" + "--" + Name + "外交背景：" + ImpBackgroundImage1 + ", " + ImpBackgroundImage2 + ", " + ImpBackgroundImage3
    def AddTrait(self):# 在LeaderTraitData里寻找
        self.Traits.append(self.Type)
        for index, row in LeaderTraitData.iterrows():
            if row.iloc[1] == self.ShortType:
                # 从第3列开始的非NaN值
                for trait in row.dropna().tolist()[2:]:
                    localType = FindFirstColBySecondCol(NewCivdata, trait)
                    if CommonPrefix.get(localType):
                        self.Traits.append(CommonPrefix[localType] + Prefix + GetMidfix(localType) + trait)

class Leaders:
    def __init__(self, params): # params 是 DataFrame
        self.Leaders = []
        for index, row in params.iterrows():
            self.Leaders.append(Leader(row))
    def GetTypes(self):
        Types = []
        for leader in self.Leaders:
            if leader.Type not in Types:
                Types.append(leader.Type)
        return GetTypeRows(Types, "KIND_LEADER", True)
    def GetTraits(self):
        Types = []
        for leader in self.Leaders:
            if leader.Type not in Types:
                Types.append(leader.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetLeader(self):
        rows = []
        for leader in self.Leaders:
            rows.append(leader.GetLeaderRows())
        return SQLValues("Leaders", LeadersRows) + convert_to_comma_newline(rows)
    def GetLeaderQuotes(self):
        rows = []
        for leader in self.Leaders:
            rows.append(leader.GetLeaderQuotesRows())
        return SQLValues("LeaderQuotes", LeaderQuotesRows) + convert_to_comma_newline(rows)
    def GetLeaderTraits(self):
        rows = []
        for leader in self.Leaders:
            if leader.GetLeaderTraitRows() != '':
                rows.append(leader.GetLeaderTraitRows())
        return SQLValues("LeaderTraits", LeaderTraitsRows) + convert_to_comma_newline(rows)
    def GetLoadingInfo(self):
        rows = []
        for leader in self.Leaders:
            rows.append(leader.GetLoadingInfoRows())
        return SQLValues("LoadingInfo", LoadingInfoRows) + convert_to_comma_newline(rows)
    # 注释：给出领袖的外交图片名字
    def GetDiplomacyImages(self):
        rows = []
        for leader in self.Leaders:
            rows.append(leader.GetDiplomacyImage())
        return "\n".join(rows)
# 领袖文件主函数:
def LeaderMain():
    if len(LeaderData) == 0:
        return
    LeadersData = Leaders(LeaderData)
    LeaderSQL = []
    LeaderSQL.append('-- Types and Traits')
    LeaderSQL.append(LeadersData.GetTypes())
    LeaderSQL.append(LeadersData.GetTraits())
    LeaderSQL.append('-- Leaders')
    LeaderSQL.append(LeadersData.GetLeader())
    LeaderSQL.append('-- Leader Quotes')
    LeaderSQL.append(LeadersData.GetLeaderQuotes())
    LeaderSQL.append('-- Leader Traits')
    LeaderSQL.append(LeadersData.GetLeaderTraits())
    LeaderSQL.append('-- Loading Info')
    LeaderSQL.append(LeadersData.GetLoadingInfo())
    LeaderSQL.append('-- Diplomacy Images')
    LeaderSQL.append(LeadersData.GetDiplomacyImages())
    LeaderSQLStr = '\n\n'.join(LeaderSQL)
    LeaderFile = FilePath + "\\" + fileName + "_Leaders.sql"
    with open(LeaderFile, "w", encoding="utf-8") as f:
        f.write(LeaderSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# Config
# Config 主函数:
def ConfigMain():
    if len(CivData) == 0 or len(LeaderData) == 0:
        return
    CivsData = Civs(CivData)
    ConfigSQL = []
    ConfigSQL.append('-- Players')
    ConfigSQL.append(CivsData.GetPlayerRows())
    ConfigSQL.append('-- Player Items')
    ConfigSQL.append(CivsData.GetPlayerItemRows())
    ConfigSQLStr = '\n\n'.join(ConfigSQL)
    ConfigFile = FilePath + "\\" + fileName + "_Configs.sql"
    with open(ConfigFile, "w", encoding="utf-8") as f:
        f.write(ConfigSQLStr)
     
# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# Icons
# 获得IconTextureAtlases表
def GetIconTextureAtlases():
    Rows = []
    def Support(Type, sizes):
        row = []
        for size in sizes:
            row.append(xmlitem(f"Name=\"ATLAS_{Type}\" IconSize=\"{size}\" Filename=\"ICON_{Type}_{size}\""))
        Rows.append("\n".join(row))
        Rows.append("\n")  # 空行
    # 文明
    for index, row in CivData.iterrows():
        Support(CommonPrefix["文明"] + Prefix + GetMidfix("文明") + str(row.iloc[1]), CivilizationSize)
    # 领袖
    for index, row in LeaderData.iterrows():
        Support(CommonPrefix["领袖"] + Prefix + GetMidfix("领袖") + str(row.iloc[1]), LeaderSize)
    # 区域
    for index, row in DistrictData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["区域"] + Prefix + GetMidfix("区域") + str(row.iloc[1]), DistrictSize)
    # 建筑
    for index, row in BuildingData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["建筑"] + Prefix + GetMidfix("建筑") + str(row.iloc[1]), BuildingSize)
    # 单位
    for index, row in UnitData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + str(row.iloc[1]), UnitSize)
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + str(row.iloc[1]) + '_PORTRAIT', UnitPortraitSize)
        elif row.iloc[5] == 2: # FromIcon列是2
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + str(row.iloc[1]), UnitSize)
    # 改良
    for index, row in ImprovementData.iterrows():#第二列都是简称
        Support(CommonPrefix["改良"] + Prefix + GetMidfix("改良") + str(row.iloc[1]), ImprovementSize)
    # 项目 这个不太一样，这个是第一行的第三列开始是简称，只在第一行，但是这个表不一定有内容
    ProjectData = []
    try:
        ProjectData = Projectdata.columns[2:].dropna().tolist()
    except:
        ProjectData = []
    if len(ProjectData) > 0:
        for project in ProjectData:
            Support(CommonPrefix["项目"] + Prefix + GetMidfix("项目") + project, ProjectSize)
    # 总督 这个表不一定有内容
    GovernorData = []
    try:
        GovernorData = Governordata.columns[2:].dropna().tolist()
    except:
        GovernorData = []
    if len(GovernorData) > 0:
        for governor in GovernorData:
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}", GovernorSize2)
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}_FILL", GovernorSize)
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}_SLOT", GovernorSize)
    return xmltab("\n".join(Rows), "IconTextureAtlases")

# 获得IconDefinitions表
def GetIconDefinitions():
    Rows = []
    def Support(Type):
        Rows.append(xmlitem(f"Name=\"ICON_{Type}\" Atlas=\"ATLAS_{Type}\" Index=\"0\""))
    # 文明
    for index, row in CivData.iterrows():
        Support(CommonPrefix["文明"] + Prefix + GetMidfix("文明") + row.iloc[1])
    # 领袖
    for index, row in LeaderData.iterrows():
        Support(CommonPrefix["领袖"] + Prefix + GetMidfix("领袖") + row.iloc[1])
        Rows.append("\n")  # 空行
    # 区域
    for index, row in DistrictData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["区域"] + Prefix + GetMidfix("区域") + row.iloc[1])
    # 建筑
    for index, row in BuildingData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["建筑"] + Prefix + GetMidfix("建筑") + row.iloc[1])
    # 单位
    for index, row in UnitData.iterrows():#第二列都是简称
        if row.iloc[5] == 0: # FromIcon列是0
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1])
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1] + '_PORTRAIT')
        elif row.iloc[5] == 2: # FromIcon列是2
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1])
    # 改良
    for index, row in ImprovementData.iterrows():#第二列都是简称
        Support(CommonPrefix["改良"] + Prefix + GetMidfix("改良") + row.iloc[1])
    # 项目 这个不太一样，这个是第一行的第三列开始是简称，只在第一行
    ProjectData = []
    try:
        ProjectData = Projectdata.columns[2:].dropna().tolist()
    except:
        ProjectData = []
    if len(ProjectData) > 0:
        for project in ProjectData:
            Support(CommonPrefix["项目"] + Prefix + GetMidfix("项目") + project)
    # 总督 这个表不一定有内容
    GovernorData = []
    try:
        GovernorData = Governordata.columns[2:].dropna().tolist()
    except:
        GovernorData = []
    if len(GovernorData) > 0:
        for governor in GovernorData:
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}")
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}_FILL")
            Support(f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{governor}_SLOT")
    return xmltab("\n".join(Rows), 'IconDefinitions')

# 获得IconAliases表
def GetIconAliases():
    Rows = []
    def Support(To,From):
        if From == 0:
            raise ValueError(f"在IconAliases中，{To}的来源不能为0")
        Rows.append(xmlitem(f"Name=\"ICON_{To}\" OtherName=\"ICON_{From}\""))
    # 区域
    for index, row in DistrictData.iterrows():#第二列都是简称
        if row.iloc[5] == 1: # FromIcon列是1, #来源是7列
            Support(CommonPrefix["区域"] + Prefix + GetMidfix("区域") + row.iloc[1], row.iloc[6])
    # 建筑
    for index, row in BuildingData.iterrows():#第二列都是简称
        if row.iloc[5] == 1: # FromIcon列是1, #来源是7列
            Support(CommonPrefix["建筑"] + Prefix + GetMidfix("建筑") + row.iloc[1], row.iloc[6])
    # 单位
    for index, row in UnitData.iterrows():#第二列都是简称
        if row.iloc[5] == 1: # FromIcon列是1, #来源是7列
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1], row.iloc[6])
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1] + '_PORTRAIT', row.iloc[6] + '_PORTRAIT')
        elif row.iloc[5] == 2: # FromIcon列是2, #来源是7列
            Support(CommonPrefix["单位"] + Prefix + GetMidfix("单位") + row.iloc[1] + '_PORTRAIT', row.iloc[6] + '_PORTRAIT')
    if len(Rows) == 0:
        return ""
    return xmltab("\n".join(Rows), 'IconAliases')

# Icon文件主函数:
def IconMain():
    IconXML = []
    IconXML.append(GetIconTextureAtlases())
    IconXML.append(GetIconDefinitions())
    IconXML.append(GetIconAliases())
    IconXMLStr = format_xml(xml("\n\n".join(IconXML)))
    IconFile = FilePath + "\\" + fileName + "_Icons.xml"
    with open(IconFile, "w", encoding="utf-8") as f:
        f.write(IconXMLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 区域
class District:
    def __init__(self, params): # params 是 DataFrame 的一行
        self.ShortType = str(params.iloc[1])
        self.Type = CommonPrefix["区域"] + Prefix + GetMidfix("区域") + self.ShortType
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Icon = 'ICON_' + self.Type
        self.IsTrait = params.iloc[2] == 1
        self.FromData = params.iloc[3]
        self.Replace = params.iloc[4] == 1
        self.FromIcon = params.iloc[5] == 1
        self.FromArtdef = params.iloc[6]
        self.NameText = RN(params.iloc[7])
        self.DescriptionText = RN(params.iloc[8])
        self.Pedia = []
        self.IsNew = self.FromData == 0
        self.Districts = [] # Districts表的数据
        self.Districts_XP2 = [] # Districts_XP2表的数据
        self.District_GreatPersonPoints = [] # District_GreatPersonPoints表的数据
        self.District_TradeRouteYields = [] # District_TradeRouteYields表的数据
        self.District_CitizenYieldChanges = [] # District_CitizenYieldChanges表的数据
        if self.IsNew:
            self.AddData()
    def Support(self, TableName):# 给出From语句
        return f" FROM {TableName} WHERE DistrictType = '{self.FromData}'"
    def AddData(self):# 在Districtdata里寻找
        eData = get_column_by_header(Districtdata, self.ShortType)
        eBaseData = get_column_by_header(Districtdata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在区域 {self.ShortType} 中，未在数据表中找到")
        self.Districts.append(self.Type) # DistrictType
        self.Districts.append(self.Name) # Name
        self.Districts.append(self.Description) # Description
        self.Districts.append('TRAIT_' + self.Type if self.IsTrait else 'NULL') # TraitType
        # 下面开始就要判断是不是NaN了,如果是NaN就用默认参数
        for i in range(0, 36): 
            if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                self.Districts.append(eBaseData[i])
            elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                self.Districts.append('NULL')
            else:
                self.Districts.append(eData[i])
        # 接下来是Districts_XP2表
        # 值得注意的是，如果全是NaN，就不插入
        if not all(pd.isna(eData[i]) for i in range(37, 42)):
            self.Districts_XP2.append(self.Type) # DistrictType
            for i in range(37, 42): 
                if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                    self.Districts_XP2.append(eBaseData[i])
                else:
                    self.Districts_XP2.append(eData[i])
        # 接下来是District_GreatPersonPoints表，不同的是，如果是NaN值就不插入
        for i in range(43, 52): 
            if not pd.isna(eData[i]):
                self.District_GreatPersonPoints.append([self.Type, GREATPERSON[i - 44], eData[i]])
        # 接下来是District_TradeRouteYields表，在第55到72列，不同的是，每三行为一组，只要有1个不是NaN值就插入
        for i in range(53, 71, 3): # 每三列为一组
            if not pd.isna(eData[i]) or not pd.isna(eData[i + 1]) or not pd.isna(eData[i + 2]):
                # 为NaN值就用0
                yield1 = eData[i] if not pd.isna(eData[i]) else 0
                yield2 = eData[i + 1] if not pd.isna(eData[i + 1]) else 0
                yield3 = eData[i + 2] if not pd.isna(eData[i + 2]) else 0
                self.District_TradeRouteYields.append([self.Type, YIELDTYPE[i // 3 - 18], yield1, yield2, yield3])
        # 接下来是District_CitizenYieldChanges表,其实就是6列，不是NaN就不插入
        for i in range(71, 77): 
            if not pd.isna(eData[i]):
                self.District_CitizenYieldChanges.append([self.Type, YIELDTYPE[i - 72], eData[i]])
    def GetDistrictReplacesRows(self):
        if self.Replace:
            try:
                return ListToSQLTuple([self.Type, self.FromData])
            except:
                raise ValueError(f"在区域 {self.ShortType} 中，Replace被选中，但是FromData为空")
    def GetDistrictRows(self):
        if not self.IsNew:
            table = DistrictsRows.copy()
            table[0] = "'" + self.Type + "'"
            table[1] = "'" + self.Name + "'"
            table[2] = "'" + self.Description + "'"
            table[3] = "'" + 'TRAIT_' + self.Type + "'" if self.IsTrait else 'NULL'
            return ListToSQLSelectNewLine(table) + self.Support("Districts")
        return ListToSQLTupleNewLine(self.Districts)
    def GetDistrict_XP2Rows(self):
        if not self.IsNew:
            table = Districts_XP2Rows.copy()
            table[0] = "'" + self.Type + "'"
            return ListToSQLSelect(table) + self.Support("Districts_XP2")
        if len(self.Districts_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Districts_XP2)
    def GetDistrict_GreatPersonPointsRows(self):
        if not self.IsNew:
            table = District_GreatPersonPointsRows.copy()
            table[0] = "'" + self.Type + "'"
            return ListToSQLSelect(table) + self.Support("District_GreatPersonPoints")
        rows = []
        for item in self.District_GreatPersonPoints:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetDistrict_TradeRouteYieldsRows(self):
        if not self.IsNew:
            table = District_TradeRouteYieldsRows.copy()
            table[0] = "'" + self.Type + "'"
            return ListToSQLSelect(table) + self.Support("District_TradeRouteYields")
        rows = []
        for item in self.District_TradeRouteYields:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetDistrict_CitizenYieldChangesRows(self):
        if not self.IsNew:
            table = District_CitizenYieldChangesRows.copy()
            table[0] = "'" + self.Type + "'"
            return ListToSQLSelect(table) + self.Support("District_CitizenYieldChanges")
        rows = []
        for item in self.District_CitizenYieldChanges:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetDistrict_AdjacenciesRows(self):
        if not self.IsNew:
            table = District_AdjacenciesRows.copy()
            table[0] = "'" + self.Type + "'"
            return ListToSQLSelect(table) + self.Support("District_Adjacencies")
        return '' # 这个表没有新建区域的数据

class Districts:
    def __init__(self, params): # params 是 DataFrame
        self.Districts = []
        for index, row in params.iterrows():
            self.Districts.append(District(row))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        TypesNoTrait = []
        for district in self.Districts:
            if district.IsTrait:
                if district.Type not in Types:
                    Types.append(district.Type)
            else:
                if district.Type not in TypesNoTrait:
                    TypesNoTrait.append(district.Type)
        if len(Types) > 0 and len(TypesNoTrait) > 0:
            return GetTypeRows(Types, "KIND_DISTRICT", True) + '\n' + GetTypeRows(TypesNoTrait, "KIND_DISTRICT", False)
        elif len(Types) > 0:
            return GetTypeRows(Types, "KIND_DISTRICT", True)
        elif len(TypesNoTrait) > 0:
            return GetTypeRows(TypesNoTrait, "KIND_DISTRICT", False)
    def GetTraits(self):
        Types = []
        for district in self.Districts:
            if district.Type not in Types and district.IsTrait:
                Types.append(district.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetDistrictReplaces(self):
        Values = [] # 只会出现Values
        for district in self.Districts:
            if district.Replace and district.GetDistrictReplacesRows() != '':
                Values.append(district.GetDistrictReplacesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("DistrictReplaces", DistrictReplacesRows) + convert_to_comma_newline(Values)
    def GetDistrict(self):
        Values = []
        Selects = []
        for district in self.Districts:
            if district.IsNew and district.GetDistrictRows() != '':
                Values.append(district.GetDistrictRows())
            elif not district.IsNew and district.GetDistrictRows() != '':
                Selects.append(district.GetDistrictRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValuesNewLine("Districts", DistrictsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelectNewLine("Districts", DistrictsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetDistrict_XP2(self):
        Values = []
        Selects = []
        for district in self.Districts:
            if district.IsNew and district.GetDistrict_XP2Rows() != '':
                Values.append(district.GetDistrict_XP2Rows())
            elif not district.IsNew and district.GetDistrict_XP2Rows() != '':
                Selects.append(district.GetDistrict_XP2Rows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Districts_XP2", Districts_XP2Rows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Districts_XP2", Districts_XP2Rows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetDistrict_GreatPersonPoints(self):
        Values = []
        Selects = []
        for district in self.Districts:
            if district.IsNew and district.GetDistrict_GreatPersonPointsRows() != '':
                Values.append(district.GetDistrict_GreatPersonPointsRows())
            elif not district.IsNew and district.GetDistrict_GreatPersonPointsRows() != '':
                Selects.append(district.GetDistrict_GreatPersonPointsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("District_GreatPersonPoints", District_GreatPersonPointsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("District_GreatPersonPoints", District_GreatPersonPointsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetDistrict_TradeRouteYields(self):
        Values = []
        Selects = []
        for district in self.Districts:
            if district.IsNew and district.GetDistrict_TradeRouteYieldsRows() != '':
                Values.append(district.GetDistrict_TradeRouteYieldsRows())
            elif not district.IsNew and district.GetDistrict_TradeRouteYieldsRows() != '':
                Selects.append(district.GetDistrict_TradeRouteYieldsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("District_TradeRouteYields", District_TradeRouteYieldsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("District_TradeRouteYields", District_TradeRouteYieldsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetDistrict_CitizenYieldChanges(self):
        Values = []
        Selects = []
        for district in self.Districts:
            if district.IsNew and district.GetDistrict_CitizenYieldChangesRows() != '':
                Values.append(district.GetDistrict_CitizenYieldChangesRows())
            elif not district.IsNew and district.GetDistrict_CitizenYieldChangesRows() != '':
                Selects.append(district.GetDistrict_CitizenYieldChangesRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("District_CitizenYieldChanges", District_CitizenYieldChangesRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("District_CitizenYieldChanges", District_CitizenYieldChangesRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetDistrict_Adjacencies(self):
        Selects = [] # 只会出现Select
        for district in self.Districts:
            if not district.IsNew and district.GetDistrict_AdjacenciesRows() != '':
                Selects.append(district.GetDistrict_AdjacenciesRows())
        if len(Selects) == 0:
            return ''
        return SQLSelect("District_Adjacencies", District_AdjacenciesRows) + '\n' + '\nUNION '.join(Selects) + ';'

# 区域文件主函数:
def DistrictMain():
    if len(DistrictData) == 0:
        return
    DistrictsData = Districts(DistrictData)
    DistrictSQL = []
    DistrictSQL.append('-- Types and Traits')
    DistrictSQL.append(DistrictsData.GetTypes())
    DistrictSQL.append(DistrictsData.GetTraits())
    DistrictSQL.append('-- District Replaces')
    DistrictSQL.append(DistrictsData.GetDistrictReplaces())
    DistrictSQL.append('-- Districts')
    DistrictSQL.append(DistrictsData.GetDistrict())
    DistrictSQL.append('-- Districts_XP2')
    DistrictSQL.append(DistrictsData.GetDistrict_XP2())
    DistrictSQL.append('-- District_GreatPersonPoints')
    DistrictSQL.append(DistrictsData.GetDistrict_GreatPersonPoints())
    DistrictSQL.append('-- District_TradeRouteYields')
    DistrictSQL.append(DistrictsData.GetDistrict_TradeRouteYields())
    DistrictSQL.append('-- District_CitizenYieldChanges')
    DistrictSQL.append(DistrictsData.GetDistrict_CitizenYieldChanges())
    DistrictSQL.append('-- District_Adjacencies')
    DistrictSQL.append(DistrictsData.GetDistrict_Adjacencies())
    DistrictSQLStr = '\n\n'.join(DistrictSQL)
    DistrictFile = FilePath + "\\" + fileName + "_Districts.sql"
    with open(DistrictFile, "w", encoding="utf-8") as f:
        f.write(DistrictSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 建筑
class Building:
    def __init__(self, params): # params 是 DataFrame 的一行 为了提高兼容性，不再使用 str1 + str2 的形式，避免数字无效
        self.ShortType = str(params.iloc[1])
        self.Type = f"{CommonPrefix['建筑']}{Prefix}{GetMidfix('建筑')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Icon = f"ICON_{self.Type}"
        self.IsTrait = params.iloc[2] == 1
        self.FromData = params.iloc[3]
        self.Replace = params.iloc[4] == 1
        self.FromIcon = params.iloc[5] == 1
        self.FromArtdef = params.iloc[6]
        self.NameText = RN(params.iloc[7])
        self.DescriptionText = RN(params.iloc[8])
        self.Pedia = []
        self.IsNew = self.FromData == 0
        self.Buildings = [] # Buildings表的数据
        self.Buildings_XP2 = [] # Building_YieldChanges表的数据
        self.Building_YieldChanges = [] # Building_YieldChanges表的数据
        self.Building_GreatPersonPoints = [] # Building_GreatPersonPoints表的数据
        self.Building_YieldChangesBonusWithPower = [] # Building_YieldChangesBonusWithPower表的数据
        self.Building_CitizenYieldChanges = [] # Building_CitizenYieldChanges表的数据
        self.Building_TourismBombs_XP2 = [] # Building_TourismBombs_XP2表的数据
        self.Building_YieldDistrictCopies = [] # Building_YieldDistrictCopies表的数据
        self.Building_YieldsPerEra = [] # Building_YieldsPerEra表的数据
        self.BuildingPrereqs = [] # BuildingPrereqs表的数据
        self.Building_YieldDistrictCopiesRows = [] # Building_YieldDistrictCopiesRows表的数据
        if self.IsNew:
            self.AddData()
    def Support(self, TableName):# 给出From语句
        return f" FROM {TableName} WHERE BuildingType = '{self.FromData}'"
    def AddData(self):# 在Buildingdata里寻找
        eData = get_column_by_header(Buildingdata, self.ShortType)
        eBaseData = get_column_by_header(Buildingdata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在建筑 {self.ShortType} 中，未在数据表中找到")
        #['BuildingType','Name','Description','TraitType','PrereqTech','PrereqCivic','Cost','MaxPlayerInstances','MaxWorldInstances','Capital','PrereqDistrict','AdjacentDistrict','RequiresPlacement','RequiresRiver','OuterDefenseHitPoints','Housing','Entertainment','AdjacentResource','Coast','EnabledByReligion','AllowsHolyCity','PurchaseYield','MustPurchase','Maintenance','OuterDefenseStrength','CitizenSlots','MustBeLake','MustNotBeLake','RegionalRange','AdjacentToMountain','ObsoleteEra','RequiresReligion','GrantFortification','DefenseModifier','RequiresAdjacentRiver','MustBeAdjacentLand','AdvisorType','AdjacentCapital','AdjacentImprovement','CityAdjacentTerrain','UnlocksGovernmentPolicy','GovernmentTierRequirement']
        self.Buildings.append(self.Type) # BuildingType
        self.Buildings.append(self.Name) # Name
        self.Buildings.append(self.Description) # Description
        self.Buildings.append('TRAIT_' + self.Type if self.IsTrait else 'NULL') # TraitType
        # 下面开始就要判断是不是NaN了,如果是NaN就用默认参数，默认参数为NaN就用NULL
        for i in range(0, 38):
            if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                self.Buildings.append(eBaseData[i])
            elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                self.Buildings.append('NULL')
            else:
                self.Buildings.append(eData[i])
        # 接下来是Buildings_XP2表，12行,默认参数为NaN就用NULL
        if not all(pd.isna(eData[i]) for i in range(38, 50)):
            self.Buildings_XP2.append(self.Type) # BuildingType
            for i in range(38, 50):
                if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                    self.Buildings_XP2.append(eBaseData[i])
                elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                    self.Buildings_XP2.append('NULL')
                else:
                    self.Buildings_XP2.append(eData[i])
        # 接下来是BuildingPrereqs表,其实就1行，不为NaN就插入
        if not pd.isna(eData[50]):
            self.BuildingPrereqs.append([self.Type, eData[50]])
        # 接下来是Building_GreatPersonPoints表,其实就是9列，不是NaN就不插入
        for i in range(52, 61): 
            if not pd.isna(eData[i]):
                self.Building_GreatPersonPoints.append([self.Type, GREATPERSON[i - 52], eData[i]])
        # 接下来是Building_CitizenYieldChanges表,6行，不是NaN就不插入
        for i in range(61, 67): 
            if not pd.isna(eData[i]):
                self.Building_CitizenYieldChanges.append([self.Type, YIELDTYPE[i - 61], eData[i]])
        # 接下来是Building_YieldChanges表, 6行，不是NaN就不插入
        for i in range(67, 73):
            if not pd.isna(eData[i]):
                self.Building_YieldChanges.append([self.Type, eData[i], YIELDTYPE[i - 67]])
        # 接下来是Building_YieldChangesBonusWithPower表, 6行，不是NaN就不插入
        for i in range(73, 79):
            if not pd.isna(eData[i]):
                self.Building_YieldChangesBonusWithPower.append([self.Type, YIELDTYPE[i - 73], eData[i]])
        # 接下来是Building_YieldDistrictCopiesRows表，2行，都不是NaN就插入
        if not pd.isna(eData[79]) and not pd.isna(eData[80]):
            self.Building_YieldDistrictCopiesRows.append([self.Type, YIELDTYPE[eData[79]], YIELDTYPE[eData[80]]])
        # 接下来是Building_YieldsPerEra表, 6行，不是NaN就不插入
        for i in range(81, 87):
            if not pd.isna(eData[i]):
                self.Building_YieldsPerEra.append([self.Type, YIELDTYPE[i - 81], eData[i]])
        # 接下来是Building_TourismBombs_XP2表, 1行，不是NaN就不插入
        if not pd.isna(eData[87]):
            self.Building_TourismBombs_XP2.append([self.Type, eData[87]])
    def GetBuildingReplacesRows(self):
        if self.Replace:
            try:
                return ListToSQLTuple([self.Type, self.FromData])
            except:
                raise ValueError(f"在建筑 {self.ShortType} 中，Replace被选中，但是FromData为空")
    def GetBuildingsRows(self):
        if not self.IsNew:
            table = BuildingsRows.copy()
            table[0] = f"'{self.Type}'"
            table[1] = f"'{self.Name}'"
            table[2] = f"'{self.Description}'"
            table[3] = f"'{ 'TRAIT_' + self.Type }'" if self.IsTrait else 'NULL'
            return ListToSQLSelectNewLine(table) + self.Support("Buildings")
        return ListToSQLTupleNewLine(self.Buildings)
    def GetBuildings_XP2Rows(self):
        if not self.IsNew:
            table = BuildingXP2Rows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Buildings_XP2")
        if len(self.Buildings_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Buildings_XP2)
    def GetBuildingPrereqsRows(self):
        if not self.IsNew:
            if len(self.BuildingPrereqs) == 0:
                return ''
            table = BuildingPrereqsRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + f"FROM BuildingPrereqs WHERE Building = '{self.FromData}'"
        rows = []
        for item in self.BuildingPrereqs:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_GreatPersonPointsRows(self):
        if not self.IsNew:
            if len(self.Building_GreatPersonPoints) == 0:
                return ''
            table = BuildingGreatPersonPointsRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_GreatPersonPoints")
        rows = []
        for item in self.Building_GreatPersonPoints:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_CitizenYieldChangesRows(self):
        if not self.IsNew:
            if len(self.Building_CitizenYieldChanges) == 0:
                return ''
            table = BuildingCitizenYieldChangesRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_CitizenYieldChanges")
        rows = []
        for item in self.Building_CitizenYieldChanges:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_YieldChangesRows(self):
        if not self.IsNew:
            if len(self.Building_YieldChanges) == 0:
                return ''
            table = BuildingYieldChangesRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_YieldChanges")
        rows = []
        for item in self.Building_YieldChanges:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_YieldChangesBonusWithPowerRows(self):
        if not self.IsNew:
            if len(self.Building_YieldChangesBonusWithPower) == 0:
                return ''
            table = BuildingYieldChangesBonusWithPowerRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_YieldChangesBonusWithPower")
        rows = []
        for item in self.Building_YieldChangesBonusWithPower:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_TourismBombs_XP2Rows(self):
        if not self.IsNew:
            if len(self.Building_TourismBombs_XP2) == 0:
                return ''
            table = BuildingTourismBombs_XP2Rows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_TourismBombs_XP2")
        rows = []
        for item in self.Building_TourismBombs_XP2:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_YieldDistrictCopiesRows(self):
        if not self.IsNew:
            if len(self.Building_YieldDistrictCopiesRows) == 0:
                return ''
            table = Building_YieldDistrictCopiesRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_YieldDistrictCopies")
        rows = []
        for item in self.Building_YieldDistrictCopiesRows:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetBuilding_YieldsPerEraRows(self):
        if not self.IsNew:
            if len(self.Building_YieldsPerEra) == 0:
                return ''
            table = Building_YieldsPerEraRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Building_YieldsPerEra")
        rows = []
        for item in self.Building_YieldsPerEra:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Buildings:
    def __init__(self, params): # params 是 DataFrame
        self.Buildings = []
        for index, row in params.iterrows():
            self.Buildings.append(Building(row))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        TypesNoTrait = []
        for building in self.Buildings:
            if building.IsTrait:
                if building.Type not in Types:
                    Types.append(building.Type)
            else:
                if building.Type not in TypesNoTrait:
                    TypesNoTrait.append(building.Type)
        if len(Types) > 0 and len(TypesNoTrait) > 0:
            return GetTypeRows(Types, "KIND_BUILDING", True) + '\n' + GetTypeRows(TypesNoTrait, "KIND_BUILDING", False)
        elif len(Types) > 0:
            return GetTypeRows(Types, "KIND_BUILDING", True)
        elif len(TypesNoTrait) > 0:
            return GetTypeRows(TypesNoTrait, "KIND_BUILDING", False)
    def GetTraits(self):
        Types = []
        for building in self.Buildings:
            if building.IsTrait and building.Type not in Types:
                Types.append(building.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetBuildingReplaces(self):
        Values = [] # 只会出现Values
        for building in self.Buildings:
            if building.Replace and building.GetBuildingReplacesRows() != '':
                Values.append(building.GetBuildingReplacesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("BuildingReplaces", BuildingReplacesRows) + convert_to_comma_newline(Values)
    def GetBuildings(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuildingsRows() != '':
                Values.append(building.GetBuildingsRows())
            elif not building.IsNew and building.GetBuildingsRows() != '':
                Selects.append(building.GetBuildingsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValuesNewLine("Buildings", BuildingsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelectNewLine("Buildings", BuildingsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuildings_XP2(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuildings_XP2Rows() != '':
                Values.append(building.GetBuildings_XP2Rows())
            elif not building.IsNew and building.GetBuildings_XP2Rows() != '':
                Selects.append(building.GetBuildings_XP2Rows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Buildings_XP2", BuildingXP2Rows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Buildings_XP2", BuildingXP2Rows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuildingPrereqs(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuildingPrereqsRows() != '':
                Values.append(building.GetBuildingPrereqsRows())
            elif not building.IsNew and building.GetBuildingPrereqsRows() != '':
                Selects.append(building.GetBuildingPrereqsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("BuildingPrereqs", BuildingPrereqsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("BuildingPrereqs", BuildingPrereqsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_GreatPersonPoints(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_GreatPersonPointsRows() != '':
                Values.append(building.GetBuilding_GreatPersonPointsRows())
            elif not building.IsNew and building.GetBuilding_GreatPersonPointsRows() != '':
                Selects.append(building.GetBuilding_GreatPersonPointsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_GreatPersonPoints", BuildingGreatPersonPointsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_GreatPersonPoints", BuildingGreatPersonPointsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_CitizenYieldChanges(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_CitizenYieldChangesRows() != '':
                Values.append(building.GetBuilding_CitizenYieldChangesRows())
            elif not building.IsNew and building.GetBuilding_CitizenYieldChangesRows() != '':
                Selects.append(building.GetBuilding_CitizenYieldChangesRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_CitizenYieldChanges", BuildingCitizenYieldChangesRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_CitizenYieldChanges", BuildingCitizenYieldChangesRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_YieldChanges(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_YieldChangesRows() != '':
                Values.append(building.GetBuilding_YieldChangesRows())
            elif not building.IsNew and building.GetBuilding_YieldChangesRows() != '':
                Selects.append(building.GetBuilding_YieldChangesRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_YieldChanges", BuildingYieldChangesRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_YieldChanges", BuildingYieldChangesRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_YieldChangesBonusWithPower(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_YieldChangesBonusWithPowerRows() != '':
                Values.append(building.GetBuilding_YieldChangesBonusWithPowerRows())
            elif not building.IsNew and building.GetBuilding_YieldChangesBonusWithPowerRows() != '':
                Selects.append(building.GetBuilding_YieldChangesBonusWithPowerRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_YieldChangesBonusWithPower", BuildingYieldChangesBonusWithPowerRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_YieldChangesBonusWithPower", BuildingYieldChangesBonusWithPowerRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_TourismBombs_XP2(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_TourismBombs_XP2Rows() != '':
                Values.append(building.GetBuilding_TourismBombs_XP2Rows())
            elif not building.IsNew and building.GetBuilding_TourismBombs_XP2Rows() != '':
                Selects.append(building.GetBuilding_TourismBombs_XP2Rows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_TourismBombs_XP2", BuildingTourismBombs_XP2Rows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_TourismBombs_XP2", BuildingTourismBombs_XP2Rows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_YieldDistrictCopies(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_YieldDistrictCopiesRows() != '':
                Values.append(building.GetBuilding_YieldDistrictCopiesRows())
            elif not building.IsNew and building.GetBuilding_YieldDistrictCopiesRows() != '':
                Selects.append(building.GetBuilding_YieldDistrictCopiesRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_YieldDistrictCopies", Building_YieldDistrictCopiesRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_YieldDistrictCopies", Building_YieldDistrictCopiesRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetBuilding_YieldsPerEra(self):
        Values = []
        Selects = []
        for building in self.Buildings:
            if building.IsNew and building.GetBuilding_YieldsPerEraRows() != '':
                Values.append(building.GetBuilding_YieldsPerEraRows())
            elif not building.IsNew and building.GetBuilding_YieldsPerEraRows() != '':
                Selects.append(building.GetBuilding_YieldsPerEraRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Building_YieldsPerEra", Building_YieldsPerEraRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Building_YieldsPerEra", Building_YieldsPerEraRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
# 建筑文件主函数:
def BuildingMain():
    if len(BuildingData) == 0:
        return
    BuildingsData = Buildings(BuildingData)
    BuildingSQL = []
    BuildingSQL.append('-- Types and Traits')
    BuildingSQL.append(BuildingsData.GetTypes())
    BuildingSQL.append(BuildingsData.GetTraits())
    BuildingSQL.append('-- Building Replaces')
    BuildingSQL.append(BuildingsData.GetBuildingReplaces())
    BuildingSQL.append('-- Buildings')
    BuildingSQL.append(BuildingsData.GetBuildings())
    BuildingSQL.append('-- Buildings_XP2')
    BuildingSQL.append(BuildingsData.GetBuildings_XP2())
    BuildingSQL.append('-- BuildingPrereqs')
    BuildingSQL.append(BuildingsData.GetBuildingPrereqs())
    BuildingSQL.append('-- Building_GreatPersonPoints')
    BuildingSQL.append(BuildingsData.GetBuilding_GreatPersonPoints())
    BuildingSQL.append('-- Building_CitizenYieldChanges')
    BuildingSQL.append(BuildingsData.GetBuilding_CitizenYieldChanges())
    BuildingSQL.append('-- Building_YieldChanges')
    BuildingSQL.append(BuildingsData.GetBuilding_YieldChanges())
    BuildingSQL.append('-- Building_YieldChangesBonusWithPower')
    BuildingSQL.append(BuildingsData.GetBuilding_YieldChangesBonusWithPower())
    BuildingSQL.append('-- Building_TourismBombs_XP2')
    BuildingSQL.append(BuildingsData.GetBuilding_TourismBombs_XP2())
    BuildingSQL.append('-- Building_YieldDistrictCopies')
    BuildingSQL.append(BuildingsData.GetBuilding_YieldDistrictCopies())
    BuildingSQL.append('-- Building_YieldsPerEra')
    BuildingSQL.append(BuildingsData.GetBuilding_YieldsPerEra())
    BuildingSQLStr = '\n\n'.join(BuildingSQL)
    BuildingFile = FilePath + "\\" + fileName + "_Buildings.sql"
    with open(BuildingFile, "w", encoding="utf-8") as f:
        f.write(BuildingSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 单位
class Unit:
    def __init__(self, params): # params 是 DataFrame 的一行 为了提高兼容性，不再使用 str1 + str2 的形式，避免数字无效
        self.ShortType = str(params.iloc[1])
        self.Type = f"{CommonPrefix['单位']}{Prefix}{GetMidfix('单位')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Icon = f"ICON_{self.Type}"
        self.IsTrait = params.iloc[2] == 1
        self.FromData = params.iloc[3]
        self.Replace = params.iloc[4] == 1
        self.FromIcon = params.iloc[5]
        self.FromArtdef = params.iloc[6]
        self.NameText = RN(params.iloc[7])
        self.DescriptionText = RN(params.iloc[8])
        self.Pedia = []
        self.IsNew = self.FromData == 0
        self.UnitAiInfos = [] # UnitAiInfos表的数据
        self.Tags = [] # Tags表的数据
        self.TypeTags = [] # TypeTags表的数据
        self.Units = [] # Units表的数据
        self.Units_XP2 = [] # Units_XP2表的数据
        self.UnitUpgrades = [] # UnitUpgrades表的数据
        self.Units_MODE = [] # Units_MODE表的数据
        self.UnitCaptures = [] # UnitCaptures表的数据
        self.UnitReplaces = [] # UnitReplaces表的数据
        if self.IsNew:
            self.AddData()
    def Support(self, TableName):# 给出From语句
        return f" FROM {TableName} WHERE UnitType = '{self.FromData}'"
    def AddData(self):# 在Unitdata里寻找
        eData = get_column_by_header(Unitdata, self.ShortType)
        eBaseData = get_column_by_header(Unitdata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在单位 {self.ShortType} 中，未在数据表中找到")
        #['UnitType','Name','Description','TraitType','BaseSightRange','BaseMoves','Combat','RangedCombat','Range','Bombard','Domain','FormationClass','Cost','PopulationCost','FoundCity','FoundReligion','MakeTradeRoute','EvangelizeBelief','LaunchInquisition','RequiresInquisition','BuildCharges','ReligiousStrength','ReligionEvictPercent','SpreadCharges','ReligiousHealCharges','ExtractsArtifacts','Flavor','CanCapture','CanRetreatWhenCaptured','AllowBarbarians','CostProgressionModel','CostProgressionParam1','PromotionClass','InitialLevel','NumRandomChoices','PrereqTech','PrereqCivic','PrereqDistrict','PrereqPopulation','LeaderType','CanTrain','StrategicResource','PurchaseYield','MustPurchase','Maintenance','Stackable','AirSlots','CanTargetAir','PseudoYieldType','ZoneOfControl','AntiAirCombat','Spy','WMDCapable','ParkCharges','IgnoreMoves','TeamVisibility','ObsoleteTech','ObsoleteCivic','MandatoryObsoleteTech','MandatoryObsoleteCivic','AdvisorType', 'EnabledByReligion', 'TrackReligion', 'DisasterCharges', 'UseMaxMeleeTrainedStrength', 'ImmediatelyName', 'CanEarnExperience']
        self.Units.append(self.Type) # UnitType
        self.Units.append(self.Name) # Name
        self.Units.append(self.Description) # Description
        self.Units.append('TRAIT_' + self.Type if self.IsTrait else 'NULL') # TraitType
        # 下面开始就要判断是不是NaN了,如果是NaN就用默认参数，默认参数为NaN就用NULL，63行
        for i in range(0, 63):
            if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                self.Units.append(eBaseData[i])
            elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                self.Units.append('NULL')
            else:
                self.Units.append(eData[i])
        # 接下来是Units_XP2表，10行,默认参数为NaN就用NULL
        if not all(pd.isna(eData[i]) for i in range(63, 73)):
            self.Units_XP2.append(self.Type) # UnitType
            for i in range(63, 73):
                if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                    self.Units_XP2.append(eBaseData[i])
                elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                    self.Units_XP2.append('NULL')
                else:
                    self.Units_XP2.append(eData[i])
        # 接下来是Units_MODE表,其实就1行，不为NaN就插入
        if not pd.isna(eData[73]):
            self.Units_MODE.append([self.Type, eData[73]])
        # 接下来是UnitReplaces表
        if not pd.isna(eData[74]):
            self.UnitReplaces = [self.Type, eData[74]]
        # 接下来是UnitUpgrades表,其实就1行，不为NaN就插入
        if not pd.isna(eData[75]):
            self.UnitUpgrades.append([self.Type, eData[75]])
        # 接下来是UnitCaptures表,其实就1行，不为NaN就插入
        if not pd.isna(eData[76]):
            self.UnitCaptures.append([self.Type, eData[76]])
        # 接下来是UnitAiInfos表, 22行，为NaN就不插入，否则插入默认参数
        for i in range(78, 100): 
            if not pd.isna(eData[i]):
                self.UnitAiInfos.append([self.Type, eBaseData[i]])
        # 接下来是TypeTags表, 39行，为NaN就不插入，否则插入默认参数
        for i in range(101, 140): 
            if not pd.isna(eData[i]):
                self.TypeTags.append([self.Type, eBaseData[i]])
        # 如果为特色单位， 直接插入TypeTags表
        if self.IsTrait:
            self.TypeTags.append([self.Type, f"CLASS_{Prefix}{GetMidfix('单位')}{self.ShortType}"])
    def GetUnitReplacesRows(self):
        if self.IsNew:
            if self.UnitReplaces != []:
                return ListToSQLTuple(self.UnitReplaces)
            return ''
         # 旧单位才需要更新这个表
        if self.Replace:
            try:
                return ListToSQLTuple([self.Type, self.FromData])
            except:
                raise ValueError(f"在单位 {self.ShortType} 中，Replace被选中，但是FromData为空")
    def GetUnitsRows(self):
        if not self.IsNew:
            table = UnitsRows.copy()
            table[0] = f"'{self.Type}'"
            table[1] = f"'{self.Name}'"
            table[2] = f"'{self.Description}'"
            table[3] = f"'{ 'TRAIT_' + self.Type }'" if self.IsTrait else 'NULL'
            return ListToSQLSelectNewLine(table) + self.Support("Units")
        return ListToSQLTupleNewLine(self.Units)
    def GetUnits_XP2Rows(self):
        if not self.IsNew:
            table = UnitsXP2Rows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("Units_XP2")
        if len(self.Units_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Units_XP2)
    def GetUnits_MODERows(self):
        if not self.IsNew:
            return '' # 这个表不必要更新
        rows = []
        if len(self.Units_MODE) == 0:
            return ''
        for item in self.Units_MODE:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetUnitUpgradesRows(self):
        if not self.IsNew:
            table = UnitUpgradesRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + f" FROM UnitUpgrades WHERE Unit = '{self.FromData}'"
        rows = []
        if len(self.UnitUpgrades) == 0:
            return ''
        for item in self.UnitUpgrades:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetUnitCapturesRows(self):
        if not self.IsNew:
            return '' # 这个表不必要更新
        rows = []
        if len(self.UnitCaptures) == 0:
            return ''
        for item in self.UnitCaptures:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetUnitAiInfosRows(self):
        if not self.IsNew:
            table = UnitAiInfosRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + self.Support("UnitAiInfos")
        rows = []
        if len(self.UnitAiInfos) == 0:
            return ''
        for item in self.UnitAiInfos:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetTagsRows(self):
        if not self.IsTrait:
            return '' # 这个表不必要更新
         # 特色单位直接插入Tags表
        tag = [f"CLASS_{Prefix}{GetMidfix('单位')}{self.ShortType}", "ABILITY_CLASS"]
        return ListToSQLTuple(tag)
    def GetTypeTagsRows(self):
        if not self.IsNew:
            table = TypeTagsRows.copy()
            table[0] = f"'{self.Type}'"
            return ListToSQLSelect(table) + f" FROM TypeTags WHERE Type = '{self.FromData}'"
        rows = []
        if len(self.TypeTags) == 0:
            return ''
        for item in self.TypeTags:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Units:
    def __init__(self, params): # params 是 DataFrame
        self.Units = []
        for index, row in params.iterrows():
            self.Units.append(Unit(row))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        TypesNoTrait = []
        for unit in self.Units:
            if unit.IsTrait:
                if unit.Type not in Types:
                    Types.append(unit.Type)
            else:
                if unit.Type not in TypesNoTrait:
                    TypesNoTrait.append(unit.Type)
        if len(Types) > 0 and len(TypesNoTrait) > 0:
            return GetTypeRows(Types, "KIND_UNIT", True) + '\n' + GetTypeRows(TypesNoTrait, "KIND_UNIT", False)
        elif len(Types) > 0:
            return GetTypeRows(Types, "KIND_UNIT", True)
        elif len(TypesNoTrait) > 0:
            return GetTypeRows(TypesNoTrait, "KIND_UNIT", False)
    def GetTraits(self):
        Types = []
        for unit in self.Units:
            if unit.IsTrait and unit.Type not in Types:
                Types.append(unit.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetUnitReplaces(self):
        Values = [] # 只会出现Values
        for unit in self.Units:
            if unit.GetUnitReplacesRows() != '' and  unit.GetUnitReplacesRows() != None:
                Values.append(unit.GetUnitReplacesRows())
        if len(Values) == 0:
            return ''
        print(Values)
        return SQLValues("UnitReplaces", UnitReplacesRows) + convert_to_comma_newline(Values)
    def GetUnits(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnitsRows() != '':
                Values.append(unit.GetUnitsRows())
            elif not unit.IsNew and unit.GetUnitsRows() != '':
                Selects.append(unit.GetUnitsRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValuesNewLine("Units", UnitsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelectNewLine("Units", UnitsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetUnits_XP2(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnits_XP2Rows() != '':
                Values.append(unit.GetUnits_XP2Rows())
            elif not unit.IsNew and unit.GetUnits_XP2Rows() != '':
                Selects.append(unit.GetUnits_XP2Rows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Units_XP2", UnitsXP2Rows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Units_XP2", UnitsXP2Rows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetUnits_MODE(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnits_MODERows() != '':
                Values.append(unit.GetUnits_MODERows())
            elif not unit.IsNew and unit.GetUnits_MODERows() != '':
                Selects.append(unit.GetUnits_MODERows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("Units_MODE", Units_MODERows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("Units_MODE", Units_MODERows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetUnitUpgrades(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnitUpgradesRows() != '':
                Values.append(unit.GetUnitUpgradesRows())
            elif not unit.IsNew and unit.GetUnitUpgradesRows() != '':
                Selects.append(unit.GetUnitUpgradesRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("UnitUpgrades", UnitUpgradesRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("UnitUpgrades", UnitUpgradesRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetUnitCaptures(self):
        Values = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnitCapturesRows() != '':
                Values.append(unit.GetUnitCapturesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("UnitCaptures", UnitCapturesRows) + convert_to_comma_newline(Values)
    def GetUnitAiInfos(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetUnitAiInfosRows() != '':
                Values.append(unit.GetUnitAiInfosRows())
            elif not unit.IsNew and unit.GetUnitAiInfosRows() != '':
                Selects.append(unit.GetUnitAiInfosRows())
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("UnitAiInfos", UnitAiInfosRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("UnitAiInfos", UnitAiInfosRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
    def GetTags(self):
        Values = []
        for unit in self.Units:
            if unit.IsTrait and unit.GetTagsRows() != '':
                Values.append(unit.GetTagsRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Tags", TagsRows) + convert_to_comma_newline(Values)
    def GetTypeTags(self):
        Values = []
        Selects = []
        for unit in self.Units:
            if unit.IsNew and unit.GetTypeTagsRows() != '':
                Values.append(unit.GetTypeTagsRows())
            elif not unit.IsNew and unit.GetTypeTagsRows() != '':
                Selects.append(unit.GetTypeTagsRows())
                if unit.IsTrait: # 特色单位还要加上Tags
                    tag = [unit.Type, f"CLASS_{Prefix}{GetMidfix('单位')}{unit.ShortType}"]
                    Values.append(ListToSQLTuple(tag))
        ValuesSQL = ''
        SelectsSQL = ''
        if len(Values) > 0:
            ValuesSQL = SQLValues("TypeTags", TypeTagsRows) + convert_to_comma_newline(Values)
        if len(Selects) > 0:
            SelectsSQL = SQLSelect("TypeTags", TypeTagsRows) + '\n' + '\nUNION '.join(Selects) + ';'
        return self.support(ValuesSQL, SelectsSQL)
# 单位文件主函数:
def UnitMain():
    if len(UnitData) == 0:
        return
    UnitsData = Units(UnitData)
    UnitSQL = []
    UnitSQL.append('-- Types and Traits')
    UnitSQL.append(UnitsData.GetTypes())
    UnitSQL.append(UnitsData.GetTraits())
    UnitSQL.append('-- UnitAiInfos')
    UnitSQL.append(UnitsData.GetUnitAiInfos())
    UnitSQL.append('-- Tags')
    UnitSQL.append(UnitsData.GetTags())
    UnitSQL.append('-- TypeTags')
    UnitSQL.append(UnitsData.GetTypeTags())
    UnitSQL.append('-- Unit Replaces')
    UnitSQL.append(UnitsData.GetUnitReplaces())
    UnitSQL.append('-- Units')
    UnitSQL.append(UnitsData.GetUnits())
    UnitSQL.append('-- Units_XP2')
    UnitSQL.append(UnitsData.GetUnits_XP2())
    UnitSQL.append('-- Units_MODE')
    UnitSQL.append(UnitsData.GetUnits_MODE())
    UnitSQL.append('-- UnitUpgrades')
    UnitSQL.append(UnitsData.GetUnitUpgrades())
    UnitSQL.append('-- UnitCaptures')
    UnitSQL.append(UnitsData.GetUnitCaptures())
    UnitSQLStr = '\n\n'.join(UnitSQL)
    UnitFile = FilePath + "\\" + fileName + "_Units.sql"
    with open(UnitFile, "w", encoding="utf-8") as f:
        f.write(UnitSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 从下面开始，不再有SELECT语句，全部是VALUES语句
# 改良设施
class Improvement:
    def __init__(self, params): # params 是 DataFrame 的一行 为了提高兼容性，不再使用 str1 + str2 的形式，避免数字无效
        self.ShortType = str(params.iloc[1])
        self.Type = f"{CommonPrefix['改良']}{Prefix}{GetMidfix('改良')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Icon = f"ICON_{self.Type}"
        self.IsTrait = params.iloc[2] == 1
        self.FromArtdef = params.iloc[6]
        self.NameText = RN(params.iloc[7])
        self.DescriptionText = RN(params.iloc[8])
        self.Pedia = []
        self.Improvements = [] # Improvements表的数据
        self.Improvements_XP2 = [] # Improvements_XP2表的数据
        self.Improvement_ValidBuildUnits = [] # Improvement_ValidBuildUnits表的数据
        self.Improvement_YieldChanges = [] # Improvement_YieldChanges表的数据
        self.Improvement_ValidTerrains = [] # Improvement_ValidTerrains表的数据
        self.Improvement_ValidFeatures = [] # Improvement_ValidFeatures表的数据
        self.Improvement_Tourisms = [] # Improvement_Tourisms表的数据
        self.AddData()
    def AddData(self):# 在Improvementdata里寻找
        eData = get_column_by_header(Improvementdata, self.ShortType)
        eBaseData = get_column_by_header(Improvementdata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在改良设施 {self.ShortType} 中，未在数据表中找到")
        self.Improvements.append(self.Type) # ImprovementType
        self.Improvements.append(self.Name) # Name
        self.Improvements.append(self.Description) # Description
        self.Improvements.append('TRAIT_' + self.Type if self.IsTrait else 'NULL') # TraitType
        self.Improvements.append(self.Icon) # Icon
        # 下面开始就要判断是不是NaN了,如果是NaN就用默认参数，默认参数为NaN就用NULL，43行
        for i in range(0, 43):
            if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                self.Improvements.append(eBaseData[i])
            elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                self.Improvements.append('NULL')
            else:
                self.Improvements.append(eData[i])
        # 接下来是Improvements_XP2表，4行,默认参数为NaN就用NULL
        if not all(pd.isna(eData[i]) for i in range(43, 47)):
            self.Improvements_XP2.append(self.Type) # ImprovementType
            for i in range(43, 47):
                if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                    self.Improvements_XP2.append(eBaseData[i])
                elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                    self.Improvements_XP2.append('NULL')
                else:
                    self.Improvements_XP2.append(eData[i])
        # 接下来是Improvement_ValidBuildUnits表, 3行，为NaN就不插入，第一个就插入默认参数，第2,3个就直接插入参数（非NaN）
        if not all(pd.isna(eData[i]) for i in range(48, 51)):
            if not pd.isna(eData[48]):
                self.Improvement_ValidBuildUnits.append([self.Type, eBaseData[48]])
            if not pd.isna(eData[49]):
                self.Improvement_ValidBuildUnits.append([self.Type, eData[49]])
            if not pd.isna(eData[50]):
                self.Improvement_ValidBuildUnits.append([self.Type, eData[50]])
        # 接下来是Improvement_YieldChanges表, 6行，为NaN就插入默认数值
        for i in range(52, 58): 
            if pd.isna(eData[i]):
                self.Improvement_YieldChanges.append([self.Type, YIELDTYPE[i-52], 0])
            else:
                self.Improvement_YieldChanges.append([self.Type, YIELDTYPE[i-52], eData[i]])
        # 接下来是Improvement_Tourism表, 4行，第一行为NaN就不插入，后3行为NaN就插入默认数值，默认参数为NaN就用NULL
        if not pd.isna(eData[59]):
            row = []
            row.append(self.Type)
            row.append(eData[59])
            for i in range(60, 63): 
                if pd.isna(eData[i]) and not pd.isna(eBaseData[i]):
                    row.append(eBaseData[i])
                elif pd.isna(eData[i]) and pd.isna(eBaseData[i]):
                    row.append('NULL')
                else:
                    row.append(eData[i])
            self.Improvement_Tourisms.append(row)
        # 接下来是Improvement_ValidTerrains表, 17行，为NaN就不插入，否则插入默认参数
        for i in range(64, 81): 
            if not pd.isna(eData[i]):
                self.Improvement_ValidTerrains.append([self.Type, eBaseData[i]])
        # 接下来是Improvement_ValidFeatures表, 11行，为NaN就不插入，否则插入默认参数
        for i in range(81, 92): 
            if not pd.isna(eData[i]):
                self.Improvement_ValidFeatures.append([self.Type, eBaseData[i]])
    def GetImprovementsRows(self):
        return ListToSQLTupleNewLine(self.Improvements)
    def GetImprovements_XP2Rows(self):
        if len(self.Improvements_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Improvements_XP2)
    def GetImprovement_ValidBuildUnitsRows(self):
        if len(self.Improvement_ValidBuildUnits) == 0:
            return ''
        rows = []
        for item in self.Improvement_ValidBuildUnits:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetImprovement_YieldChangesRows(self):
        if len(self.Improvement_YieldChanges) == 0:
            return ''
        rows = []
        for item in self.Improvement_YieldChanges:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetImprovement_ValidTerrainsRows(self):
        if len(self.Improvement_ValidTerrains) == 0:
            return ''
        rows = []
        for item in self.Improvement_ValidTerrains:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetImprovement_ValidFeaturesRows(self):
        if len(self.Improvement_ValidFeatures) == 0:
            return ''
        rows = []
        for item in self.Improvement_ValidFeatures:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetImprovement_TourismsRows(self):
        if len(self.Improvement_Tourisms) == 0:
            return ''
        rows = []
        for item in self.Improvement_Tourisms:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Improvements:
    def __init__(self, params): # params 是 DataFrame
        self.Improvements = []
        for index, row in params.iterrows():
            self.Improvements.append(Improvement(row))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        TypesNoTrait = []
        for improvement in self.Improvements:
            if improvement.IsTrait:
                if improvement.Type not in Types:
                    Types.append(improvement.Type)
            else:
                if improvement.Type not in TypesNoTrait:
                    TypesNoTrait.append(improvement.Type)
        if len(Types) > 0 and len(TypesNoTrait) > 0:
            return GetTypeRows(Types, "KIND_IMPROVEMENT", True) + '\n' + GetTypeRows(TypesNoTrait, "KIND_IMPROVEMENT", False)
        elif len(Types) > 0:
            return GetTypeRows(Types, "KIND_IMPROVEMENT", True)
        elif len(TypesNoTrait) > 0:
            return GetTypeRows(TypesNoTrait, "KIND_IMPROVEMENT", False)
    def GetTraits(self):
        Types = []
        for improvement in self.Improvements:
            if improvement.IsTrait and improvement.Type not in Types:
                Types.append(improvement.Type)
        return GetTraitRows(Types) if len(Types) > 0 else ''
    def GetImprovements(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovementsRows() != '':
                Values.append(improvement.GetImprovementsRows())
        if len(Values) == 0:
            return ''
        return SQLValuesNewLine("Improvements", ImprovementsRows) + convert_to_comma_newline(Values)
    def GetImprovements_XP2(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovements_XP2Rows() != '':
                Values.append(improvement.GetImprovements_XP2Rows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvements_XP2", Improvements_XP2Rows) + convert_to_comma_newline(Values)
    def GetImprovement_ValidBuildUnits(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovement_ValidBuildUnitsRows() != '':
                Values.append(improvement.GetImprovement_ValidBuildUnitsRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvement_ValidBuildUnits", Improvement_ValidBuildUnitsRows) + convert_to_comma_newline(Values)
    def GetImprovement_YieldChanges(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovement_YieldChangesRows() != '':
                Values.append(improvement.GetImprovement_YieldChangesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvement_YieldChanges", Improvement_YieldChangesRows) + convert_to_comma_newline(Values)
    def GetImprovement_ValidTerrains(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovement_ValidTerrainsRows() != '':
                Values.append(improvement.GetImprovement_ValidTerrainsRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvement_ValidTerrains", Improvement_ValidTerrainsRows) + convert_to_comma_newline(Values)
    def GetImprovement_ValidFeatures(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovement_ValidFeaturesRows() != '':
                Values.append(improvement.GetImprovement_ValidFeaturesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvement_ValidFeatures", Improvement_ValidFeaturesRows) + convert_to_comma_newline(Values)
    def GetImprovement_Tourisms(self):
        Values = []
        for improvement in self.Improvements:
            if improvement.GetImprovement_TourismsRows() != '':
                Values.append(improvement.GetImprovement_TourismsRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Improvement_Tourism", Improvement_TourismsRows) + convert_to_comma_newline(Values)
# 改良设施文件主函数:
def ImprovementMain():
    if len(ImprovementData) == 0:
        return
    ImprovementsData = Improvements(ImprovementData)
    ImprovementSQL = []
    ImprovementSQL.append('-- Types and Traits')
    ImprovementSQL.append(ImprovementsData.GetTypes())
    ImprovementSQL.append(ImprovementsData.GetTraits())
    ImprovementSQL.append('-- Improvements')
    ImprovementSQL.append(ImprovementsData.GetImprovements())
    ImprovementSQL.append('-- Improvements_XP2')
    ImprovementSQL.append(ImprovementsData.GetImprovements_XP2())
    ImprovementSQL.append('-- Improvement_ValidBuildUnits')
    ImprovementSQL.append(ImprovementsData.GetImprovement_ValidBuildUnits())
    ImprovementSQL.append('-- Improvement_YieldChanges')
    ImprovementSQL.append(ImprovementsData.GetImprovement_YieldChanges())
    ImprovementSQL.append('-- Improvement_ValidTerrains')
    ImprovementSQL.append(ImprovementsData.GetImprovement_ValidTerrains())
    ImprovementSQL.append('-- Improvement_ValidFeatures')
    ImprovementSQL.append(ImprovementsData.GetImprovement_ValidFeatures())
    ImprovementSQL.append('-- Improvement_Tourism')
    ImprovementSQL.append(ImprovementsData.GetImprovement_Tourisms())
    ImprovementSQLStr = '\n\n'.join(ImprovementSQL)
    ImprovementFile = f"{FilePath}\\{fileName}_Improvements.sql"
    with open(ImprovementFile, "w", encoding="utf-8") as f:
        f.write(ImprovementSQLStr)
                
# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 总督
# 所有数据都在 Governordata 里，NewCivdata只有文明和领袖绑定
class Governor:
    def __init__(self, ShortType): # params 是 DataFrame 的一行 为了提高兼容性，不再使用 str1 + str2 的形式，避免数字无效
        eData = get_column_by_header(Governordata, ShortType)
        BaseData = get_column_by_header(Governordata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在总督 {ShortType} 中，未在数据表中找到")
        self.ShortType = str(ShortType)
        self.Type = f"{CommonPrefix['总督']}{Prefix}{GetMidfix('总督')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        self.Title = f"LOC_{self.Type}_TITLE"
        self.ShortTitle = f"LOC_{self.Type}_SHORT_TITLE"
        self.Image = f"{self.Type}_NORMAL"
        self.PortraitImage = f"{self.Type}_NORMAL"
        self.PortraitImageSelected = f"{self.Type}_SELECTED"
        self.IsTrait = not pd.isna(eData[2]) # TraitType不为NaN就是特色总督
        # 下面按照顺序读取信息
        self.TextName = RN(eData[0]) # NameText
        self.TextDescription = RN(eData[1]) # DescriptionText
        self.TraitType = f"TRAIT_{self.Type}" if not pd.isna(eData[2]) else 'NULL' # TraitType
        self.TextTitle = RN(eData[3]) if not pd.isna(eData[3]) else '' # TitleText
        self.TextShortTitle = RN(eData[4]) if not pd.isna(eData[4]) else '' # ShortTitleText
        self.IdentityPressure = eData[5] if not pd.isna(eData[5]) else BaseData[5] # IdentityPressure
        self.TransitionStrength = eData[6] if not pd.isna(eData[6]) else BaseData[6] # TransitionStrength
        self.AssignCityState = eData[7] if not pd.isna(eData[7]) else BaseData[7] # AssignCityState
        self.AssignToMajor = eData[8] if not pd.isna(eData[8]) else '' # AssignToMajor
        # 下面是晋升
        self.BaseName = RN(eData[10]) # BaseName
        self.BaseDescription = RN(eData[11]) # BaseDescription
        self.L1Name = RN(eData[12]) if not pd.isna(eData[12]) else '' # L1Name
        self.L1Description = RN(eData[13]) if not pd.isna(eData[13]) else '' # L1Description
        self.M1Name = RN(eData[14]) if not pd.isna(eData[14]) else '' # M1Name
        self.M1Description = RN(eData[15]) if not pd.isna(eData[15]) else '' # M1Description
        self.R1Name = RN(eData[16]) if not pd.isna(eData[16]) else '' # R1Name
        self.R1Description = RN(eData[17]) if not pd.isna(eData[17]) else '' # R1Description
        self.L2Name = RN(eData[18]) if not pd.isna(eData[18]) else '' # L2Name
        self.L2Description = RN(eData[19]) if not pd.isna(eData[19]) else '' # L2Description
        self.M2Name = RN(eData[20]) if not pd.isna(eData[20]) else '' # M2Name
        self.M2Description = RN(eData[21]) if not pd.isna(eData[21]) else '' # M2Description
        self.R2Name = RN(eData[22]) if not pd.isna(eData[22]) else '' # R2Name
        self.R2Description = RN(eData[23]) if not pd.isna(eData[23]) else '' # R2Name
        self.L3Name = RN(eData[24]) if not pd.isna(eData[24]) else '' # L3Name
        self.L3Description = RN(eData[25]) if not pd.isna(eData[25]) else '' # L3Description
        self.M3Name = RN(eData[26]) if not pd.isna(eData[26]) else '' # M3Name
        self.M3Description = RN(eData[27]) if not pd.isna(eData[27]) else '' # M3Description
        self.R3Name = RN(eData[28]) if not pd.isna(eData[28]) else '' # R3Name
        self.R3Description = RN(eData[29]) if not pd.isna(eData[29]) else '' # R3Description
        # 下面开始构建SQL数据
        self.Types = [] # Types表的数据
        self.Traits = [] # Traits表的数据
        self.LeaderTraits = [] # LeaderTraits表的数据
        self.CivilizationTraits = [] # CivilizationTraits表的数据
        self.Governors = [] # Governors表的数据
        self.Governors_XP2 = [] # Governors_XP2表的数据
        self.GovernorPromotionSets = [] # GovernorPromotionSets表的数据
        self.GovernorPromotions = [] # GovernorPromotions表的数据
        self.GovernorPromotionPrereqs = [] # GovernorPromotionPrereqs表的数据
        self.AddData()
    def AddData(self):# 在Governordata里寻找
        self.Governors.append(self.Type) # GovernorType
        self.Governors.append(f"{self.Name}") # Name
        self.Governors.append(f"{self.Description}") # Description
        self.Governors.append(self.TraitType) # TraitType
        self.Governors.append(f"{self.Title}") # Title
        self.Governors.append(f"{self.ShortTitle}") # ShortTitle
        self.Governors.append(f"{self.Image}") # Image
        self.Governors.append(f"{self.PortraitImage}") # PortraitImage
        self.Governors.append(f"{self.PortraitImageSelected}") # PortraitImageSelected
        self.Governors.append(self.IdentityPressure) # IdentityPressure
        self.Governors.append(self.TransitionStrength) # TransitionStrength
        self.Governors.append(self.AssignCityState) # AssignCityState
        # 接下来是Governors_XP2表, 1行，直接插入
        if self.AssignToMajor != '':
            self.Governors_XP2.append(self.Type) # GovernorType
            self.Governors_XP2.append(self.AssignToMajor) # AssignToMajor
        def support(self, str, a,b,c):
            Base = f"GOVERNOR_{self.ShortType}_PROMOTION_{str}"
            BaseName, BaseDescription = GetNameDescription(Base)
            self.Types.append(Base)
            self.GovernorPromotionSets.append([self.Type, Base]) # GovernorType, GovernorPromotion
            self.GovernorPromotions.append([Base, f"{BaseName}", f"{BaseDescription}", a, b, c]) # GovernorPromotionType, Name, Description, Level, Column, BaseAbility
        if self.BaseName != '':
            support(self, "BASE", 0, 1, 1)
        if self.L1Name != '':
            support(self, "L1", 1, 0, 0)
        if self.M1Name != '':
            support(self, "M1", 1, 1, 0)
        if self.R1Name != '':
            support(self, "R1", 1, 2, 0)
        if self.L2Name != '':
            support(self, "L2", 2, 0, 0)
        if self.M2Name != '':
            support(self, "M2", 2, 1, 0)
        if self.R2Name != '':
            support(self, "R2", 2, 2, 0)
        if self.L3Name != '':
            support(self, "L3", 3, 0, 0)
        if self.M3Name != '':
            support(self, "M3", 3, 1, 0)
        if self.R3Name != '':
            support(self, "R3", 3, 2, 0)
        # 接下来是GovernorPromotionPrereqs表
        def support2(self, str1, str2):
            base = f"GOVERNOR_{self.ShortType}_PROMOTION_{str1}"
            prereq = f"GOVERNOR_{self.ShortType}_PROMOTION_{str2}"
            self.GovernorPromotionPrereqs.append([base, prereq]) # GovernorPromotionType, PrereqGovernorPromotion
        if self.L1Name != '':
            support2(self, "L1", "BASE")
            if self.L2Name != '':
                support2(self, "L2", "L1")
            if self.M2Name != '':
                support2(self, "M2", "L1")
        if self.M1Name != '':
            support2(self, "M1", "BASE")
            if self.L2Name != '':
                support2(self, "L2", "M1")
            if self.M2Name != '':
                support2(self, "M2", "M1")
            if self.R2Name != '':
                support2(self, "R2", "M1")
        if self.R1Name != '':
            support2(self, "R1", "BASE")
            if self.R2Name != '':
                support2(self, "R2", "R1")
            if self.M2Name != '':
                support2(self, "M2", "R1")
        if self.L2Name != '':
            if self.L3Name != '':
                support2(self, "L3", "L2")
            if self.M3Name != '':
                support2(self, "M3", "L2")
        if self.M2Name != '':
            if self.L3Name != '':
                support2(self, "L3", "M2")
            if self.M3Name != '':
                support2(self, "M3", "M2")
            if self.R3Name != '':
                support2(self, "R3", "M2")
        if self.R2Name != '':
            if self.R3Name != '':
                support2(self, "R3", "R2")
            if self.M3Name != '':
                support2(self, "M3", "R2")
    def GetTypes(self):
        rows = []
        rows.append(ListToSQLTuple([self.Type, "KIND_GOVERNOR"]))
        if self.TraitType != 'NULL':
            rows.append(ListToSQLTuple(['TRAIT_' + self.Type, 'KIND_TRAIT']))
        for item in self.Types:
            rows.append(ListToSQLTuple([item, "KIND_GOVERNOR_PROMOTION"]))
        return convert_to_comma_noend_newline(rows)
    def GetLeaderTraits(self):
        if self.TraitType == 'NULL':
            return ''
        LeaderTraitsRows = []
        for index, row in LeaderTraitGrovernorData.iterrows(): 
            if row.iloc[1] == self.ShortType:
                for trait in row.dropna().tolist()[2:]:
                    leader = f"{CommonPrefix['领袖']}{Prefix}{GetMidfix('领袖')}{trait}"
                    LeaderTraitsRows.append(ListToSQLTuple([leader, self.TraitType]))
        if len(LeaderTraitsRows) == 0:
            return ''
        return convert_to_comma_noend_newline(LeaderTraitsRows)
    def GetCivilizationTraits(self):
        if self.TraitType == 'NULL':
            return ''
        CivilizationTraitsRows = []
        for index, row in CivTraitGrovernorData.iterrows(): 
            if row.iloc[1] == self.ShortType:
                for trait in row.dropna().tolist()[2:]:
                    civ = f"{CommonPrefix['文明']}{Prefix}{GetMidfix('文明')}{trait}"
                    CivilizationTraitsRows.append(ListToSQLTuple([civ, self.TraitType]))
        if len(CivilizationTraitsRows) == 0:
            return ''
        return convert_to_comma_noend_newline(CivilizationTraitsRows)
    def GetTraits(self):
        if self.TraitType == 'NULL':
            return ''
        return ListToSQLTuple(['TRAIT_' + self.Type, *GetNameDescription('TRAIT_' + self.Type)])
    def GetGovernorsRows(self):
        return ListToSQLTupleNewLine(self.Governors)
    def GetGovernors_XP2(self):
        if len(self.Governors_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Governors_XP2)
    def GetGovernorPromotionSets(self):
        if len(self.GovernorPromotionSets) == 0:
            return ''
        rows = []
        for item in self.GovernorPromotionSets:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetGovernorPromotions(self):
        if len(self.GovernorPromotions) == 0:
            return ''
        rows = []
        for item in self.GovernorPromotions:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetGovernorPromotionPrereqs(self):
        if len(self.GovernorPromotionPrereqs) == 0:
            return ''
        rows = []
        for item in self.GovernorPromotionPrereqs:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Governors:
    def __init__(self, params): 
        self.Governors = []
        for governor in params:
            self.Governors.append(Governor(governor))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        for governor in self.Governors:
            Types.append(governor.GetTypes())
        if len(Types) == 0:
            return ''
        return TypeHead + convert_to_comma_newline(Types)
    def GetTraits(self):
        Values = []
        for governor in self.Governors:
            if governor.GetTraits() != '':
                Values.append(governor.GetTraits())
        if len(Values) == 0:
            return ''
        return SQLValues("Traits", TraitRows) + convert_to_comma_newline(Values)
    def GetLeaderTraits(self):
        Values = []
        for governor in self.Governors:
            if governor.GetLeaderTraits() != '':
                Values.append(governor.GetLeaderTraits())
        if len(Values) == 0:
            return ''
        return SQLValues("LeaderTraits", LeaderTraitsRows) + convert_to_comma_newline(Values)
    def GetCivilizationTraits(self):
        Values = []
        for governor in self.Governors:
            if governor.GetCivilizationTraits() != '':
                Values.append(governor.GetCivilizationTraits())
        if len(Values) == 0:
            return ''
        return SQLValues("CivilizationTraits", CivilizationTraitsRows) + convert_to_comma_newline(Values)
    def GetGovernors(self):
        Values = []
        for governor in self.Governors:
            if governor.GetGovernorsRows() != '':
                Values.append(governor.GetGovernorsRows())
        if len(Values) == 0:
            return ''
        return SQLValuesNewLine("Governors", GovernorsRows) + convert_to_comma_newline(Values)
    def GetGovernors_XP2(self):
        Values = []
        for governor in self.Governors:
            if governor.GetGovernors_XP2() != '':
                Values.append(governor.GetGovernors_XP2())
        if len(Values) == 0:
            return ''
        return SQLValues("Governors_XP2", Governors_XP2Rows) + convert_to_comma_newline(Values)
    def GetGovernorPromotionSets(self):
        Values = []
        for governor in self.Governors:
            if governor.GetGovernorPromotionSets() != '':
                Values.append(governor.GetGovernorPromotionSets())
        if len(Values) == 0:
            return ''
        return SQLValues("GovernorPromotionSets", GovernorPromotionSetsRows) + convert_to_comma_newline(Values)
    def GetGovernorPromotions(self):
        Values = []
        for governor in self.Governors:
            if governor.GetGovernorPromotions() != '':
                Values.append(governor.GetGovernorPromotions())
        if len(Values) == 0:
            return ''
        return SQLValues("GovernorPromotions", GovernorPromotionsRows) + convert_to_comma_newline(Values)
    def GetGovernorPromotionPrereqs(self):
        Values = []
        for governor in self.Governors:
            if governor.GetGovernorPromotionPrereqs() != '':
                Values.append(governor.GetGovernorPromotionPrereqs())
        if len(Values) == 0:
            return ''
        return SQLValues("GovernorPromotionPrereqs", GovernorPromotionPrereqsRows) + convert_to_comma_newline(Values)
# 总督文件主函数:
def GovernorMain():
    GovernorData = Governordata.columns[2:].dropna().tolist()
    if len(GovernorData) == 0:
        return
    GovernorsData = Governors(GovernorData)
    GovernorSQL = []
    GovernorSQL.append('-- Types and Traits')
    GovernorSQL.append(GovernorsData.GetTypes())
    GovernorSQL.append('-- Traits')
    GovernorSQL.append(GovernorsData.GetTraits())
    GovernorSQL.append('-- LeaderTraits')
    GovernorSQL.append(GovernorsData.GetLeaderTraits())
    GovernorSQL.append('-- CivilizationTraits')
    GovernorSQL.append(GovernorsData.GetCivilizationTraits())
    GovernorSQL.append('-- Governors')
    GovernorSQL.append(GovernorsData.GetGovernors())
    GovernorSQL.append('-- Governors_XP2')
    GovernorSQL.append(GovernorsData.GetGovernors_XP2())
    GovernorSQL.append('-- GovernorPromotionSets')
    GovernorSQL.append(GovernorsData.GetGovernorPromotionSets())
    GovernorSQL.append('-- GovernorPromotions')
    GovernorSQL.append(GovernorsData.GetGovernorPromotions())
    GovernorSQL.append('-- GovernorPromotionPrereqs')
    GovernorSQL.append(GovernorsData.GetGovernorPromotionPrereqs())
    GovernorSQLStr = '\n\n'.join(GovernorSQL)
    GovernorFile = f"{FilePath}\\{fileName}_Governors.sql"
    with open(GovernorFile, "w", encoding="utf-8") as f:
        f.write(GovernorSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 项目
class Project:
    def __init__(self, ShortType): # params 是 DataFrame 的一行 为了提高兼容性，不再使用 str1 + str2 的形式，避免数字无效
        eData = get_column_by_header(Projectdata, ShortType)
        BaseData = get_column_by_header(Projectdata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在项目 {ShortType} 中，未在数据表中找到")
        self.ShortType = str(ShortType)
        self.Type = f"{CommonPrefix['项目']}{Prefix}{GetMidfix('项目')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        self.ShortName = f"LOC_{self.Type}_SHORT_NAME"
        self.PopupText = f"LOC_{self.Type}_POPUP" if not pd.isna(eData[3]) else 'NULL'
        self.Icon = f"ICON_{self.Type}"
        # 下面按照顺序读取信息
        def support( str):#判断是不是nan，是就返回NULL
            return 'NULL' if pd.isna(str) else str
        self.TextName = RN(eData[0]) # Name
        self.TextShortName = RN(eData[1]) # ShortName
        self.TextDescription = RN(eData[2]) # Description
        self.TextPopup = RN(eData[3]) if not pd.isna(eData[3]) else '' # PopupText
        self.Cost = eData[4] if not pd.isna(eData[4]) else BaseData[4] # Cost
        self.CostProgressionModel = eData[5] if not pd.isna(eData[5]) else BaseData[5] # CostProgressionModel
        self.CostProgressionParam1 = eData[6] if not pd.isna(eData[6]) else BaseData[6] # CostProgressionParam1
        self.PrereqTech = eData[7] if not pd.isna(eData[7]) else support(BaseData[7]) # PrereqTech
        self.PrereqCivic = eData[8] if not pd.isna(eData[8]) else support(BaseData[8]) # PrereqCivic
        self.PrereqDistrict = eData[9] if not pd.isna(eData[9]) else support(BaseData[9]) # PrereqDistrict
        self.RequiredBuilding = eData[10] if not pd.isna(eData[10]) else support(BaseData[10]) # RequiredBuilding
        self.VisualBuildingType = eData[11] if not pd.isna(eData[11]) else support(BaseData[11]) # VisualBuildingType
        self.SpaceRace = eData[12] if not pd.isna(eData[12]) else support(BaseData[12]) # SpaceRace
        self.OuterDefenseRepair = eData[13] if not pd.isna(eData[13]) else BaseData[13] # OuterDefenseRepair
        self.MaxPlayerInstances = eData[14] if not pd.isna(eData[14]) else support(BaseData[14]) # MaxPlayerInstances
        self.AmenitiesWhileActive = eData[15] if not pd.isna(eData[15]) else BaseData[15] # AmenitiesWhileActive
        self.PrereqResource = eData[16] if not pd.isna(eData[16]) else support(BaseData[16]) # PrereqResource
        self.AdvisorType = eData[17] if not pd.isna(eData[17]) else support(BaseData[17]) # AdvisorType
        self.WMD = eData[18] if not pd.isna(eData[18]) else BaseData[18] # WMD
        self.UnlocksFromEffect = eData[19] if not pd.isna(eData[19]) else support(BaseData[19]) # UnlocksFromEffect
        # 下面是XP1表
        self.IdentityPerCitizenChange = eData[20] if not pd.isna(eData[20]) else BaseData[20] # IdentityPerCitizenChange
        # 下面是XP2表
        self.RequiredPowerWhileActive = eData[21] if not pd.isna(eData[21]) else support(BaseData[21]) # RequiredPowerWhileActive
        self.ReligiousPressureModifier = eData[22] if not pd.isna(eData[22]) else support(BaseData[22]) # ReligiousPressureModifier
        self.RequiredBuilding_XP2 = eData[23] if not pd.isna(eData[23]) else support(BaseData[23]) # RequiredBuilding
        self.CreateBuilding = eData[24] if not pd.isna(eData[24]) else support(BaseData[24]) # CreateBuilding
        self.FullyPoweredWhileActive = eData[25] if not pd.isna(eData[25]) else support(BaseData[25]) # FullyPoweredWhileActive
        self.MaxSimultaneousInstances = eData[26] if not pd.isna(eData[26]) else support(BaseData[26]) # MaxSimultaneousInstances
        # 下面是MODE表
        self.PrereqImprovement = eData[27] if not pd.isna(eData[27]) else support(BaseData[27]) # PrereqImprovement
        self.ResourceType_MODE = eData[28] if not pd.isna(eData[28]) else support(BaseData[28]) # ResourceType(Mode)
        # 下面是Project_BuildingCosts表
        self.ConsumedBuildingType = eData[29] if not pd.isna(eData[29]) else '' # ConsumedBuildingType
        # 下面开始构建SQL数据
        self.Projects = [] # Projects表的数据
        self.Projects_XP1 = [] # Projects_XP1表的数据
        self.Projects_XP2 = [] # Projects_XP2表的数据
        self.Projects_MODE = [] # Projects_MODE表的数据
        self.Project_BuildingCosts = [] # Project_BuildingCosts表的数据
        self.Project_GreatPersonPoints = [] # Project_GreatPersonPoints表的数据
        self.Project_ResourceCosts = [] # Project_ResourceCosts表的数据
        self.Project_YieldConversions = [] # Project_YieldConversions表的数据
        self.AddData()
    def AddData(self):# 在Projectdata里寻找
        eData = get_column_by_header(Projectdata, self.ShortType)
        self.Projects.append(self.Type) # ProjectType
        self.Projects.append(f"{self.Name}") # Name
        self.Projects.append(f"{self.ShortName}") # ShortName
        self.Projects.append(f"{self.Description}") # Description
        self.Projects.append(f"{self.PopupText}") # PopupText
        self.Projects.append(self.Cost) # Cost
        self.Projects.append(self.CostProgressionModel) # CostProgressionModel
        self.Projects.append(self.CostProgressionParam1) # CostProgressionParam1
        self.Projects.append(self.PrereqTech) # PrereqTech
        self.Projects.append(self.PrereqCivic) # PrereqCivic
        self.Projects.append(self.PrereqDistrict) # PrereqDistrict
        self.Projects.append(self.RequiredBuilding) # RequiredBuilding
        self.Projects.append(self.VisualBuildingType) # VisualBuildingType
        self.Projects.append(self.SpaceRace) # SpaceRace
        self.Projects.append(self.OuterDefenseRepair) # OuterDefenseRepair
        self.Projects.append(self.MaxPlayerInstances) # MaxPlayerInstances
        self.Projects.append(self.AmenitiesWhileActive) # AmenitiesWhileActive
        self.Projects.append(self.PrereqResource) # PrereqResource
        self.Projects.append(self.AdvisorType) # AdvisorType
        self.Projects.append(self.WMD) # WMD
        self.Projects.append(self.UnlocksFromEffect) # UnlocksFromEffect
        # 接下来是XP1表, 1行，直接插入
        if not pd.isna(eData[20]):
            self.Projects_XP1.append(self.Type) # ProjectType
            self.Projects_XP1.append(self.IdentityPerCitizenChange) # IdentityPerCitizenChange
        # 接下来是XP2表, 1行，直接插入（直接判断
        if not all(pd.isna(eData[i]) for i in range(21,27)):
            self.Projects_XP2.append(self.Type) # ProjectType
            self.Projects_XP2.append(self.RequiredPowerWhileActive) # RequiredPower
            self.Projects_XP2.append(self.ReligiousPressureModifier) # ReligiousPressureModifier
            self.Projects_XP2.append(self.RequiredBuilding_XP2) # RequiredBuilding
            self.Projects_XP2.append(self.CreateBuilding) # CreateBuilding
            self.Projects_XP2.append(self.FullyPoweredWhileActive) # FullyPoweredWhileActive
            self.Projects_XP2.append(self.MaxSimultaneousInstances) # MaxSimultaneousInstances
        # 接下来是MODE表, 1行，直接插入
        if not all(pd.isna(eData[i]) for i in range(27,29)):
            self.Projects_MODE.append(self.Type) # ProjectType
            self.Projects_MODE.append(self.PrereqImprovement) # PrereqImprovement
            self.Projects_MODE.append(self.ResourceType_MODE) # ResourceType(Mode)
        # 接下来是Project_BuildingCosts表
        if not pd.isna(eData[29]):
            self.Project_BuildingCosts.append(self.Type) # ProjectType
            self.Project_BuildingCosts.append(self.ConsumedBuildingType) # ConsumedBuildingType
        # 接下来是Project_GreatPersonPoints表，9行,如果不是nan就插入
        for i in range(31, 40):
            if not pd.isna(eData[i]):
                self.Project_GreatPersonPoints.append([self.Type, GREATPERSON[i-31], eData[i], 'COST_PROGRESSION_GAME_PROGRESS', 800]) # ProjectType, GreatPersonClassType, Points, PointProgressionModel, PointProgressionParam1
        # 接下来是Project_ResourceCosts表，2行,如果第一行不是nan就插入
        if not pd.isna(eData[41]):
            self.Project_ResourceCosts.append(self.Type) # ProjectType
            self.Project_ResourceCosts.append(eData[41]) # ResourceType
            self.Project_ResourceCosts.append(eData[42] if not pd.isna(eData[42]) else 0) # StartProductionCost
        # 接下来是Project_YieldConversions表，6行,如果不是nan就插入
        for i in range(43, 49):
            if not pd.isna(eData[i]):
                self.Project_YieldConversions.append([self.Type, YIELDTYPE[i-43], eData[i] if not pd.isna(eData[i]) else 0]) # ProjectType, YieldType, PercentOfProductionRate
    def GetProjectsRows(self):
        return ListToSQLTupleNewLine(self.Projects)
    def GetProjects_XP1(self):
        if len(self.Projects_XP1) == 0:
            return ''
        return ListToSQLTuple(self.Projects_XP1)
    def GetProjects_XP2(self):
        if len(self.Projects_XP2) == 0:
            return ''
        return ListToSQLTuple(self.Projects_XP2)
    def GetProjects_MODE(self):
        if len(self.Projects_MODE) == 0:
            return ''
        return ListToSQLTuple(self.Projects_MODE)
    def GetProject_BuildingCosts(self):
        if len(self.Project_BuildingCosts) == 0:
            return ''
        return ListToSQLTuple(self.Project_BuildingCosts)
    def GetProject_GreatPersonPoints(self):
        if len(self.Project_GreatPersonPoints) == 0:
            return ''
        rows = []
        for item in self.Project_GreatPersonPoints:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
    def GetProject_ResourceCosts(self):
        if len(self.Project_ResourceCosts) == 0:
            return ''
        return ListToSQLTuple(self.Project_ResourceCosts)
    def GetProject_YieldConversions(self):
        if len(self.Project_YieldConversions) == 0:
            return ''
        rows = []
        for item in self.Project_YieldConversions:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Projects:
    def __init__(self, params): 
        self.Projects = []
        for project in params:
            self.Projects.append(Project(project))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        for project in self.Projects:
            Types.append(project.Type)
        if len(Types) == 0:
            return ''
        return GetTypeRows(Types, "KIND_PROJECT", False)
    def GetProjects(self):
        Values = []
        for project in self.Projects:
            if project.GetProjectsRows() != '':
                Values.append(project.GetProjectsRows())
        if len(Values) == 0:
            return ''
        return SQLValuesNewLine("Projects", ProjectsRows) + convert_to_comma_newline(Values)
    def GetProjects_XP1(self):
        Values = []
        for project in self.Projects:
            if project.GetProjects_XP1() != '':
                Values.append(project.GetProjects_XP1())
        if len(Values) == 0:
            return ''
        return SQLValues("Projects_XP1", Projects_XP1Rows) + convert_to_comma_newline(Values)
    def GetProjects_XP2(self):
        Values = []
        for project in self.Projects:
            if project.GetProjects_XP2() != '':
                Values.append(project.GetProjects_XP2())
        if len(Values) == 0:
            return ''
        return SQLValues("Projects_XP2", Projects_XP2Rows) + convert_to_comma_newline(Values)
    def GetProjects_MODE(self):
        Values = []
        for project in self.Projects:
            if project.GetProjects_MODE() != '':
                Values.append(project.GetProjects_MODE())
        if len(Values) == 0:
            return ''
        return SQLValues("Projects_MODE", Projects_MODERows) + convert_to_comma_newline(Values)
    def GetProject_BuildingCosts(self):
        Values = []
        for project in self.Projects:
            if project.GetProject_BuildingCosts() != '':
                Values.append(project.GetProject_BuildingCosts())
        if len(Values) == 0:
            return ''
        return SQLValues("Project_BuildingCosts", Project_BuildingCostsRows) + convert_to_comma_newline(Values)
    def GetProject_GreatPersonPoints(self):
        Values = []
        for project in self.Projects:
            if project.GetProject_GreatPersonPoints() != '':
                Values.append(project.GetProject_GreatPersonPoints())
        if len(Values) == 0:
            return ''
        return SQLValues("Project_GreatPersonPoints", Project_GreatPersonPointsRows) + convert_to_comma_newline(Values)
    def GetProject_ResourceCosts(self):
        Values = []
        for project in self.Projects:
            if project.GetProject_ResourceCosts() != '':
                Values.append(project.GetProject_ResourceCosts())
        if len(Values) == 0:
            return ''
        return SQLValues("Project_ResourceCosts", Project_ResourceCostsRows) + convert_to_comma_newline(Values)
    def GetProject_YieldConversions(self):
        Values = []
        for project in self.Projects:
            if project.GetProject_YieldConversions() != '':
                Values.append(project.GetProject_YieldConversions())
        if len(Values) == 0:
            return ''
        return SQLValues("Project_YieldConversions", Project_YieldConversionsRows) + convert_to_comma_newline(Values)
# 项目文件主函数:
def ProjectMain():
    ProjectData = Projectdata.columns[2:].dropna().tolist()
    if len(ProjectData) == 0:
        return
    ProjectsData = Projects(ProjectData)
    ProjectSQL = []
    ProjectSQL.append('-- Types')
    ProjectSQL.append(ProjectsData.GetTypes())
    ProjectSQL.append('-- Projects')
    ProjectSQL.append(ProjectsData.GetProjects())
    ProjectSQL.append('-- Projects_XP1')
    ProjectSQL.append(ProjectsData.GetProjects_XP1())
    ProjectSQL.append('-- Projects_XP2')
    ProjectSQL.append(ProjectsData.GetProjects_XP2())
    ProjectSQL.append('-- Projects_MODE')
    ProjectSQL.append(ProjectsData.GetProjects_MODE())
    ProjectSQL.append('-- Project_BuildingCosts')
    ProjectSQL.append(ProjectsData.GetProject_BuildingCosts())
    ProjectSQL.append('-- Project_GreatPersonPoints')
    ProjectSQL.append(ProjectsData.GetProject_GreatPersonPoints())
    ProjectSQL.append('-- Project_ResourceCosts')
    ProjectSQL.append(ProjectsData.GetProject_ResourceCosts())
    ProjectSQL.append('-- Project_YieldConversions')
    ProjectSQL.append(ProjectsData.GetProject_YieldConversions())
    ProjectSQLStr = '\n\n'.join(ProjectSQL)
    ProjectFile = f"{FilePath}\\{fileName}_Projects.sql"
    with open(ProjectFile, "w", encoding="utf-8") as f:
        f.write(ProjectSQLStr)
        
# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 政策卡类
class Policy:
    def __init__(self, ShortType): 
        eData = get_column_by_header(Policydata, ShortType)
        BaseData = get_column_by_header(Policydata, "默认参数") # 默认参数
        if len(eData) == 0:
            raise ValueError(f"在政策卡 {ShortType} 中，未在数据表中找到")
        self.ShortType = str(ShortType)
        self.Type = f"{CommonPrefix['政策']}{Prefix}{GetMidfix('政策')}{self.ShortType}"
        self.Name, self.Description = GetNameDescription(self.Type)
        # 下面按照顺序读取信息
        def support( str):#判断是不是nan，是就返回NULL
            return 'NULL' if pd.isna(str) else str
        self.TextName = RN(eData[0]) # Name
        self.TextDescription = RN(eData[1]) # Description
        self.PrereqCivic = eData[2] if not pd.isna(eData[2]) else support(BaseData[2]) # PrereqCivic
        self.PrereqTech = eData[3] if not pd.isna(eData[3]) else support(BaseData[3]) # PrereqTech
        self.GovernmentSlotType = eData[4] if not pd.isna(eData[4]) else support(BaseData[4]) # GovernmentSlotType
        self.RequiresGovernmentUnlock = eData[5] if not pd.isna(eData[5]) else support(BaseData[5]) # RequiresGovernmentUnlock
        self.ExplicitUnlock = eData[6] if not pd.isna(eData[6]) else BaseData[6] # ExplicitUnlock
        # 下面是XP1表
        self.MinimumGameEra = eData[7] if not pd.isna(eData[7]) else support(BaseData[7]) # MinimumGameEra
        self.MaximumGameEra = eData[8] if not pd.isna(eData[8]) else support(BaseData[8]) # MaximumGameEra
        self.RequiresDarkAge = eData[9] if not pd.isna(eData[9]) else BaseData[9] # RequiresDarkAge
        self.RequiresGoldenAge = eData[10] if not pd.isna(eData[10]) else BaseData[10] # RequiresGoldenAge
        # 下面是开始构建SQL数据
        self.Policies = [] # Policies表的数据
        self.Policies_XP1 = [] # Policies_XP1表的数据
        self.Policy_GovernmentExclusives_XP2 = [] # Policy_GovernmentExclusives_XP2表的数据
        self.AddData()
    def AddData(self):# 在Policydata里寻找
        eData = get_column_by_header(Policydata, self.ShortType)
        BaseData = get_column_by_header(Policydata, "默认参数") # 默认参数
        self.Policies.append(self.Type) # PolicyType
        self.Policies.append(f"{self.Name}") # Name
        self.Policies.append(f"{self.Description}") # Description
        self.Policies.append(self.PrereqCivic) # PrereqCivic
        self.Policies.append(self.PrereqTech) # PrereqTech
        self.Policies.append(self.GovernmentSlotType) # GovernmentSlotType
        self.Policies.append(self.RequiresGovernmentUnlock) # RequiresGovernmentUnlock
        self.Policies.append(self.ExplicitUnlock) # ExplicitUnlock
        # 接下来是XP1表, 1行，直接插入
        if not all(pd.isna(eData[i]) for i in range(7,11)):
            self.Policies_XP1.append(self.Type) # PolicyType
            self.Policies_XP1.append(self.MinimumGameEra) # MinimumGameEra
            self.Policies_XP1.append(self.MaximumGameEra) # MaximumGameEra
            self.Policies_XP1.append(self.RequiresDarkAge) # RequiresDarkAge
            self.Policies_XP1.append(self.RequiresGoldenAge) # RequiresGoldenAge
        # 接下来是Policy_GovernmentExclusives_XP2表, 13行，逐行插入
        for i in range(12, 25):
            if not pd.isna(eData[i]):
                self.Policy_GovernmentExclusives_XP2.append([self.Type, BaseData[i]]) # PolicyType, GovernmentType
    def GetPoliciesRows(self):
        return ListToSQLTuple(self.Policies)
    def GetPolicies_XP1(self):
        if len(self.Policies_XP1) == 0:
            return ''
        return ListToSQLTuple(self.Policies_XP1)
    def GetPolicy_GovernmentExclusives_XP2(self):
        if len(self.Policy_GovernmentExclusives_XP2) == 0:
            return ''
        rows = []
        for item in self.Policy_GovernmentExclusives_XP2:
            rows.append(ListToSQLTuple(item))
        return convert_to_comma_noend_newline(rows)
class Policies:
    def __init__(self, params): 
        self.Policies = []
        for policy in params:
            self.Policies.append(Policy(policy))
    def support(self, str1,str2):
        if str1 != '' and str2 != '':
            return str1 + '\n\n' + str2
        elif str1 != '' and str2 == '':
            return str1
        elif str2 != '' and str1 == '':
            return str2
        else:
            return ''
    def GetTypes(self):
        Types = []
        for policy in self.Policies:
            Types.append(policy.Type)
        if len(Types) == 0:
            return ''
        return GetTypeRows(Types, "KIND_POLICY", False)
    def GetPolicies(self):
        Values = []
        for policy in self.Policies:
            if policy.GetPoliciesRows() != '':
                Values.append(policy.GetPoliciesRows())
        if len(Values) == 0:
            return ''
        return SQLValues("Policies", PoliciesRows) + convert_to_comma_newline(Values)
    def GetPolicies_XP1(self):
        Values = []
        for policy in self.Policies:
            if policy.GetPolicies_XP1() != '':
                Values.append(policy.GetPolicies_XP1())
        if len(Values) == 0:
            return ''
        return SQLValues("Policies_XP1", Policies_XP1Rows) + convert_to_comma_newline(Values)
    def GetPolicy_GovernmentExclusives_XP2(self):
        Values = []
        for policy in self.Policies:
            if policy.GetPolicy_GovernmentExclusives_XP2() != '':
                Values.append(policy.GetPolicy_GovernmentExclusives_XP2())
        if len(Values) == 0:
            return ''
        return SQLValues("Policy_GovernmentExclusives_XP2", Policy_GovernmentExclusives_XP2Rows) + convert_to_comma_newline(Values)
# 政策卡文件主函数:
def PolicyMain():
    PolicyData = Policydata.columns[2:].dropna().tolist()
    if len(PolicyData) == 0:
        return
    PoliciesData = Policies(PolicyData)
    PolicySQL = []
    PolicySQL.append('-- Types')
    PolicySQL.append(PoliciesData.GetTypes())
    PolicySQL.append('-- Policies')
    PolicySQL.append(PoliciesData.GetPolicies())
    PolicySQL.append('-- Policies_XP1')
    PolicySQL.append(PoliciesData.GetPolicies_XP1())
    PolicySQL.append('-- Policy_GovernmentExclusives_XP2')
    PolicySQL.append(PoliciesData.GetPolicy_GovernmentExclusives_XP2())
    PolicySQLStr = '\n\n'.join(PolicySQL)
    PolicyFile = f"{FilePath}\\{fileName}_Policies.sql"
    with open(PolicyFile, "w", encoding="utf-8") as f:
        f.write(PolicySQLStr)
        
# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 历史时刻
# 生成历史时刻表
def GetHistoricalMomentsRows():
    Rows = []
    if len(DistrictData) != 0:
        tDistricts = Districts(DistrictData)
        for district in tDistricts.Districts:
            Rows.append(MomentTypes('DISTRICT', district.Type))
    if len(BuildingData) != 0:
        tBuildings = Buildings(BuildingData)
        for building in tBuildings.Buildings:
            Rows.append(MomentTypes('BUILDING', building.Type))
    if len(UnitData) != 0:
        tUnits = Units(UnitData)
        for unit in tUnits.Units:
            Rows.append(MomentTypes('UNIT', unit.Type))
    if len(ImprovementData) != 0:
        tImprovements = Improvements(ImprovementData)
        for improvement in tImprovements.Improvements:
            Rows.append(MomentTypes('IMPROVEMENT', improvement.Type))
    GovernorData = Governordata.columns[2:].dropna().tolist()
    if len(GovernorData) != 0:
        GovernorsData = Governors(GovernorData)
        for governor in GovernorsData.Governors:
            Rows.append(MomentTypes('GOVERNOR', governor.Type))
    if len(Rows) == 0:
        return ''
    return SQLValues("MomentIllustrations", MomentIllustrationsRows) + convert_to_comma_newline(Rows)
# 历史时刻文件主函数:
def HistoricalMomentMain():
    HistoricalMomentSQL = []
    if GetHistoricalMomentsRows() != '':
        HistoricalMomentSQL.append('-- MomentIllustrations')
        HistoricalMomentSQL.append(GetHistoricalMomentsRows())
        HistoricalMomentSQLStr = '\n\n'.join(HistoricalMomentSQL)
        HistoricalMomentFile = f"{FilePath}\\{fileName}_Moments.sql"
        with open(HistoricalMomentFile, "w", encoding="utf-8") as f:
            f.write(HistoricalMomentSQLStr)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 文本
class Texts:
    def __init__(self): 
        self.CivilizationTexts = [] # Civilization文本的数据
        self.LeaderTexts = [] # Leader文本的数据
        self.DistrictTexts = [] # District文本的数据
        self.BuildingTexts = [] # Building文本的数据
        self.UnitTexts = [] # Unit文本的数据
        self.ImprovementTexts = [] # Improvement文本的数据
        self.GovernorTexts = [] # Governor文本的数据
        self.ProjectTexts = [] # Project文本的数据
        self.PolicyTexts = [] # Policy文本的数据
        self.CityNameTexts = [] # CityName文本的数据
        self.CitizenNameTexts = [] # CitizenName文本的数据
        self.PediaTexts = [] # Pedia文本的数据
        self.DiploText = [] # Diplo文本的数据
    def support(self, lang, Tag, Text):
        return f"('{lang}', '{Tag}', '{Text}')"
    def AddData(self, lang):
        self.lang = lang
        self.AddCivilizationTexts(lang)
        self.AddLeaderTexts(lang)
        self.AddDistrictTexts(lang)
        self.AddBuildingTexts(lang)
        self.AddUnitTexts(lang)
        self.AddImprovementTexts(lang)
        self.AddGovernorTexts(lang)
        self.AddProjectTexts(lang)
        self.AddPolicyTexts(lang)
        self.AddCityNameTexts(lang)
        self.AddCitizenNameTexts(lang)
        self.AddDiploTexts(lang)
    def AddCivilizationTexts(self, lang):
        if len(CivData) == 0:
            return # 如果没有文明数据，直接返回
        CivsData = Civs(CivData)
        for civ in CivsData.Civs:
            TraitType = f"TRAIT_{civ.Type}"
            if lang == CN:
                self.CivilizationTexts.append("-- " + civ.NameText)
                self.CivilizationTexts.append(self.support(lang, civ.Name, civ.NameText))
                self.CivilizationTexts.append(self.support(lang, civ.Description, civ.NameText))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{civ.Type}_ADJECTIVE", f"{civ.NameText}的"))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", civ.AbilityNameText))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", civ.AbilityDescriptionText))
                if PediaText:
                    i = 1
                    for para in civ.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_CIVILIZATIONS_PAGE_{civ.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1 
            else:
                self.CivilizationTexts.append(self.support(lang, civ.Name, ''))
                self.CivilizationTexts.append(self.support(lang, civ.Description, ''))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{civ.Type}_ADJECTIVE", ''))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", ''))
                self.CivilizationTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", ''))
                if PediaText:
                    i = 1
                    for para in civ.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_CIVILIZATIONS_PAGE_{civ.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def AddLeaderTexts(self, lang):
        if len(LeaderData) == 0:
            return
        LeadersData = Leaders(LeaderData)
        for leader in LeadersData.Leaders:
            TraitType = f"TRAIT_{leader.Type}"
            if lang == CN:
                self.LeaderTexts.append("-- " + leader.NameText)
                self.LeaderTexts.append(self.support(lang, leader.Name, leader.NameText))
                self.LeaderTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix("领袖") + leader.ShortType}_QUOTE", leader.QuoteText))
                self.LeaderTexts.append(self.support(lang, f"LOC_LOADING_INFO_{leader.Type}", leader.LoadingText))
                self.LeaderTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", leader.AbilityNameText))
                self.LeaderTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", leader.AbilityDescriptionText))
                self.CityNameTexts.append(self.support(lang, f"LOC_{leader.Type}_CAPITAL_NAME", leader.CapitalName))
                if PediaText:
                    i = 1
                    for para in leader.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_LEADERS_PAGE_{leader.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1
            else:
                self.LeaderTexts.append(self.support(lang, leader.Name, ''))
                self.LeaderTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix("领袖") + leader.ShortType}_QUOTE", ''))
                self.LeaderTexts.append(self.support(lang, f"LOC_LOADING_INFO_{leader.Type}", ''))
                self.LeaderTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", ''))
                self.LeaderTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", ''))
                self.CityNameTexts.append(self.support(lang, f"LOC_{leader.Type}_CAPITAL_NAME", ''))
                if PediaText:
                    i = 1
                    for para in leader.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_LEADERS_PAGE_{leader.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def AddDistrictTexts(self, lang):
        if len(DistrictData) == 0:
            return
        DistrictsData = Districts(DistrictData)
        for district in DistrictsData.Districts:
            TraitType = f"TRAIT_{district.Type}"
            if lang == CN:
                self.DistrictTexts.append("-- " + district.NameText)
                self.DistrictTexts.append(self.support(lang, district.Name, district.NameText))
                self.DistrictTexts.append(self.support(lang, district.Description, district.DescriptionText))
                if district.IsTrait:
                    self.DistrictTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ district.Name + '}'))
                    self.DistrictTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ district.Description + '}'))
                if PediaText:
                    i = 1
                    for para in district.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_DISTRICTS_PAGE_{district.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1
            else:
                self.DistrictTexts.append(self.support(lang, district.Name, ''))
                self.DistrictTexts.append(self.support(lang, district.Description, ''))
                if district.IsTrait:
                    self.DistrictTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ district.Name + '}'))
                    self.DistrictTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ district.Description + '}'))
                if PediaText:
                    i = 1
                    for para in district.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_DISTRICTS_PAGE_{district.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def AddBuildingTexts(self, lang):
        if len(BuildingData) == 0:
            return
        BuildingsData = Buildings(BuildingData)
        for building in BuildingsData.Buildings:
            TraitType = f"TRAIT_{building.Type}"
            if lang == CN:
                self.BuildingTexts.append("-- " + building.NameText)
                self.BuildingTexts.append(self.support(lang, building.Name, building.NameText))
                self.BuildingTexts.append(self.support(lang, building.Description, building.DescriptionText))
                if building.IsTrait:
                    self.BuildingTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ building.Name + '}'))
                    self.BuildingTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ building.Description + '}'))
                if PediaText:
                    i = 1
                    for para in building.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_BUILDINGS_PAGE_{building.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1
            else:
                self.BuildingTexts.append(self.support(lang, building.Name, ''))
                self.BuildingTexts.append(self.support(lang, building.Description, ''))
                if building.IsTrait:
                    self.BuildingTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ building.Name + '}'))
                    self.BuildingTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ building.Description + '}'))
                if PediaText:
                    i = 1
                    for para in building.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_BUILDINGS_PAGE_{building.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def AddUnitTexts(self, lang):
        if len(UnitData) == 0:
            return
        UnitsData = Units(UnitData)
        for unit in UnitsData.Units:
            TraitType = f"TRAIT_{unit.Type}"
            if lang == CN:
                self.UnitTexts.append("-- " + unit.NameText)
                self.UnitTexts.append(self.support(lang, unit.Name, unit.NameText))
                self.UnitTexts.append(self.support(lang, unit.Description, unit.DescriptionText))
                if unit.IsTrait:
                    self.UnitTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ unit.Name + '}'))
                    self.UnitTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ unit.Description + '}'))
                if PediaText:
                    i = 1
                    for para in unit.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_UNITS_PAGE_{unit.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1
            else:
                self.UnitTexts.append(self.support(lang, unit.Name, ''))
                self.UnitTexts.append(self.support(lang, unit.Description, ''))
                if unit.IsTrait:
                    self.UnitTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ unit.Name + '}'))
                    self.UnitTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ unit.Description + '}'))
                if PediaText:
                    i = 1
                    for para in unit.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_UNITS_PAGE_{unit.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def AddImprovementTexts(self, lang):
        if len(ImprovementData) == 0:
            return
        ImprovementsData = Improvements(ImprovementData)
        for improvement in ImprovementsData.Improvements:
            TraitType = f"TRAIT_{improvement.Type}"
            if lang == CN:
                self.ImprovementTexts.append("-- " + improvement.NameText)
                self.ImprovementTexts.append(self.support(lang, improvement.Name, improvement.NameText))
                self.ImprovementTexts.append(self.support(lang, improvement.Description, improvement.DescriptionText))
                if improvement.IsTrait:
                    self.ImprovementTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ improvement.Name + '}'))
                    self.ImprovementTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ improvement.Description + '}'))
                if PediaText:
                    i = 1
                    for para in improvement.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_IMPROVEMENTS_PAGE_{improvement.Type}_CHAPTER_HISTORY_PARA_{i}", para))
                        i += 1
            else:
                self.ImprovementTexts.append(self.support(lang, improvement.Name, ''))
                self.ImprovementTexts.append(self.support(lang, improvement.Description, ''))
                if improvement.IsTrait:
                    self.ImprovementTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ improvement.Name + '}'))
                    self.ImprovementTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ improvement.Description + '}'))
                if PediaText:
                    i = 1
                    for para in improvement.Pedia:
                        self.PediaTexts.append(self.support(lang, f"LOC_PEDIA_IMPROVEMENTS_PAGE_{improvement.Type}_CHAPTER_HISTORY_PARA_{i}", ''))
                        i += 1
    def tSupport(self, governor, str, NameText, DescriptionText):
        Base = f"GOVERNOR_{governor.ShortType}_PROMOTION_{str}"
        self.GovernorTexts.append(self.support(self.lang, f"LOC_{Base}_NAME", NameText))
        self.GovernorTexts.append(self.support(self.lang, f"LOC_{Base}_DESCRIPTION", DescriptionText))
    def AddGovernorTexts(self, lang):
        GovernorData = Governordata.columns[2:].dropna().tolist()
        if len(GovernorData) == 0:
            return
        GovernorsData = Governors(GovernorData)
        for governor in GovernorsData.Governors:
            TraitType = f"TRAIT_{governor.Type}"
            if lang == CN:
                self.GovernorTexts.append("-- " + governor.TextName)
                self.GovernorTexts.append(self.support(lang, governor.Name, governor.TextName))
                self.GovernorTexts.append(self.support(lang, governor.Description, governor.TextDescription))
                if governor.IsTrait:
                    self.GovernorTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ governor.Name + '}'))
                    self.GovernorTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ governor.Description + '}'))
                self.GovernorTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix('总督') + governor.ShortType}_TITLE", governor.TextTitle))
                self.GovernorTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix('总督') + governor.ShortType}_SHORT_TITLE", governor.TextShortTitle))
                # 下面是晋升
                self.tSupport(governor, 'BASE', governor.BaseName, governor.BaseDescription)
                if governor.L1Name != '':
                    self.tSupport(governor, 'L1', governor.L1Name, governor.L1Description)
                if governor.M1Name != '':
                    self.tSupport(governor, 'M1', governor.M1Name, governor.M1Description)
                if governor.R1Name != '':
                    self.tSupport(governor, 'R1', governor.R1Name, governor.R1Description)
                if governor.L2Name != '':
                    self.tSupport(governor, 'L2', governor.L2Name, governor.L2Description)
                if governor.M2Name != '':
                    self.tSupport(governor, 'M2', governor.M2Name, governor.M2Description)
                if governor.R2Name != '':
                    self.tSupport(governor, 'R2', governor.R2Name, governor.R2Description)
                if governor.L3Name != '':
                    self.tSupport(governor, 'L3', governor.L3Name, governor.L3Description)
                if governor.M3Name != '':
                    self.tSupport(governor, 'M3', governor.M3Name, governor.M3Description)
                if governor.R3Name != '':
                    self.tSupport(governor, 'R3', governor.R3Name, governor.R3Description)
            else:
                self.GovernorTexts.append(self.support(lang, governor.Name, ''))
                self.GovernorTexts.append(self.support(lang, governor.Description, ''))
                if governor.IsTrait:
                    self.GovernorTexts.append(self.support(lang, f"LOC_{TraitType}_NAME", '{'+ governor.Name + '}'))
                    self.GovernorTexts.append(self.support(lang, f"LOC_{TraitType}_DESCRIPTION", '{'+ governor.Description + '}'))
                self.GovernorTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix('总督') + governor.ShortType}_TITLE", ''))
                self.GovernorTexts.append(self.support(lang, f"LOC_{Prefix + GetMidfix('总督') + governor.ShortType}_SHORT_TITLE", ''))
                # 下面是晋升
                self.tSupport(governor, 'BASE', '', '')
                if governor.L1Name != '':
                    self.tSupport(governor, 'L1', '', '')
                if governor.M1Name != '':
                    self.tSupport(governor, 'M1', '', '')
                if governor.R1Name != '':
                    self.tSupport(governor, 'R1', '', '')
                if governor.L2Name != '':
                    self.tSupport(governor, 'L2', '', '')
                if governor.M2Name != '':
                    self.tSupport(governor, 'M2', '', '')
                if governor.R2Name != '':
                    self.tSupport(governor, 'R2', '', '')
                if governor.L3Name != '':
                    self.tSupport(governor, 'L3', '', '')
                if governor.M3Name != '':
                    self.tSupport(governor, 'M3', '', '')
                if governor.R3Name != '':
                    self.tSupport(governor, 'R3', '', '')
    def AddProjectTexts(self, lang):
        ProjectData = Projectdata.columns[2:].dropna().tolist()
        if len(ProjectData) == 0:
            return
        ProjectsData = Projects(ProjectData)
        for project in ProjectsData.Projects:
            if lang == CN:
                self.ProjectTexts.append("-- " + project.TextName)
                self.ProjectTexts.append(self.support(lang, project.Name, project.TextName))
                self.ProjectTexts.append(self.support(lang, project.ShortName, project.TextShortName))
                self.ProjectTexts.append(self.support(lang, project.Description, project.TextDescription))
                if project.TextPopup != '':
                    self.ProjectTexts.append(self.support(lang, project.PopupText, project.TextPopup))
            else:
                self.ProjectTexts.append(self.support(lang, project.Name, ''))
                self.ProjectTexts.append(self.support(lang, project.ShortName, ''))
                self.ProjectTexts.append(self.support(lang, project.Description, ''))
                if project.TextPopup != '':
                    self.ProjectTexts.append(self.support(lang, project.PopupText, ''))
    def AddPolicyTexts(self, lang):
        PolicyData = Policydata.columns[2:].dropna().tolist()
        if len(PolicyData) == 0:
            return
        PoliciesData = Policies(PolicyData)
        for policy in PoliciesData.Policies:
            if lang == CN:
                self.PolicyTexts.append("-- " + policy.TextName)
                self.PolicyTexts.append(self.support(lang, policy.Name, policy.TextName))
                self.PolicyTexts.append(self.support(lang, policy.Description, policy.TextDescription))
            else:
                self.PolicyTexts.append(self.support(lang, policy.Name, ''))
                self.PolicyTexts.append(self.support(lang, policy.Description, ''))
    def AddCityNameTexts(self, lang):
        if len(CivData) == 0:
            return # 如果没有文明数据，直接返回
        CivsData = Civs(CivData)
        for civ in CivsData.Civs:
            if civ.City == 0:
                continue
            if isinstance(civ.City, int) and civ.City > 0:
                i = 1
                for name in civ.CityNames:
                    if lang == CN:
                        self.CityNameTexts.append(self.support(lang, f"LOC_CITY_NAME_{Prefix + GetMidfix('文明') + civ.ShortType}_{i}", name))
                    else:
                        self.CityNameTexts.append(self.support(lang, f"LOC_CITY_NAME_{Prefix + GetMidfix('文明') + civ.ShortType}_{i}", ''))
                    i += 1
    def AddCitizenNameTexts(self, lang):
        if len(CivData) == 0:
            return # 如果没有文明数据，直接返回
        CivsData = Civs(CivData)
        for civ in CivsData.Civs:
            if not isinstance(civ.Citizen[0], (int, float)):
                continue
            if sum(civ.Citizen) == 0:
                continue
            if sum(civ.Citizen) > 0:
                i = 1
                for name in civ.CitizenNames:
                    if lang == CN:
                        self.CitizenNameTexts.append(self.support(lang, f"LOC_CITIZEN_NAME_{Prefix + GetMidfix('文明') + civ.ShortType}_{i}", name[0]))
                    else:
                        self.CitizenNameTexts.append(self.support(lang, f"LOC_CITIZEN_NAME_{Prefix + GetMidfix('文明') + civ.ShortType}_{i}", ''))
                    i += 1
    def AddDiploTexts(self, lang):
        return # 暂时不做
    def GetAllTexts(self):
        AllTexts = []
        if len(self.CivilizationTexts) != 0:
            AllTexts.append(convert_to_comma_noend_newline(self.CivilizationTexts))
        if len(self.LeaderTexts) != 0:
            AllTexts.append('-- Leader Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.LeaderTexts))
        if len(self.DistrictTexts) != 0:
            AllTexts.append('-- District Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.DistrictTexts))
        if len(self.BuildingTexts) != 0:
            AllTexts.append('-- Building Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.BuildingTexts))
        if len(self.UnitTexts) != 0:
            AllTexts.append('-- Unit Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.UnitTexts))
        if len(self.ImprovementTexts) != 0:
            AllTexts.append('-- Improvement Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.ImprovementTexts))
        if len(self.GovernorTexts) != 0:
            AllTexts.append('-- Governor Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.GovernorTexts))
        if len(self.ProjectTexts) != 0:
            AllTexts.append('-- Project Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.ProjectTexts))
        if len(self.PolicyTexts) != 0:
            AllTexts.append('-- Policy Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.PolicyTexts))
        if len(self.CityNameTexts) != 0 or len(self.CitizenNameTexts) != 0:
            AllTexts.append('-- City Name Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.CityNameTexts))
        if len(self.CitizenNameTexts) != 0:
            AllTexts.append('-- Citizen Name Texts')
            AllTexts.append(convert_to_comma_noend_newline(self.CitizenNameTexts))
        return convert_to_comma_noend_newline(AllTexts)
    def GetOtherTexts(self):
        OtherTexts = []
        if len(self.PediaTexts) != 0:
            OtherTexts.append('-- Pedia Texts')
            OtherTexts.append(convert_to_comma_noend_newline(self.PediaTexts))
        if len(self.DiploText) != 0:
            OtherTexts.append('-- Diplo Texts')
            OtherTexts.append(convert_to_comma_noend_newline(self.DiploText))
        if len(OtherTexts) == 0:
            return ''
        return convert_to_comma_noend_newline(OtherTexts)
    def ClaerAll(self):
        self.CivilizationTexts = [] # Civilization文本的数据
        self.LeaderTexts = [] # Leader文本的数据
        self.DistrictTexts = [] # District文本的数据
        self.BuildingTexts = [] # Building文本的数据
        self.UnitTexts = [] # Unit文本的数据
        self.ImprovementTexts = [] # Improvement文本的数据
        self.GovernorTexts = [] # Governor文本的数据
        self.ProjectTexts = [] # Project文本的数据
        self.PolicyTexts = [] # Policy文本的数据
        self.CityNameTexts = [] # CityName文本的数据
        self.CitizenNameTexts = [] # CitizenName文本的数据
        self.PediaTexts = [] # Pedia文本的数据
        self.DiploText = [] # Diplo文本的数据
# 文本文件主函数:
def TextMain():
    TextSQL = []
    TextsSQL = ''
    tTexts = Texts()
    TextPath = FilePath + "\\" + 'Text'
    if not os.path.exists(TextPath):
        os.makedirs(TextPath)
    tTexts.AddData(CN)
    TextSQL.append(LocalizedText)
    TextSQL.append(tTexts.GetAllTexts())
    if tTexts.GetOtherTexts() != '':
        TextSQL.append(tTexts.GetOtherTexts())
    TextsSQL = '\n'.join(TextSQL) + ';'
    TextsFile = f"{TextPath}\\{fileName}_Texts_CN.sql"
    with open(TextsFile, "w", encoding="utf-8") as f:
        f.write(TextsSQL)
    if Language >= 2:
        tTexts.ClaerAll()
        TextSQL = []
        TextsSQL = ''
        tTexts.AddData(EN)
        TextSQL.append(LocalizedText)
        TextSQL.append(tTexts.GetAllTexts())
        if tTexts.GetOtherTexts() != '':
            TextSQL.append(tTexts.GetOtherTexts())
        TextsSQL = '\n'.join(TextSQL) + ';'
        TextsFile = f"{TextPath}\\{fileName}_Texts_EN.sql"
        with open(TextsFile, "w", encoding="utf-8") as f:
            f.write(TextsSQL)
    if Language >= 3:
        tTexts.ClaerAll()
        TextSQL = []
        TextsSQL = ''
        tTexts.AddData(HK)
        TextSQL.append(LocalizedText)
        TextSQL.append(tTexts.GetAllTexts())
        if tTexts.GetOtherTexts() != '':
            TextSQL.append(tTexts.GetOtherTexts())
        TextsSQL = '\n'.join(TextSQL) + ';'
        TextsFile = f"{TextPath}\\{fileName}_Texts_HK.sql"
        with open(TextsFile, "w", encoding="utf-8") as f:
            f.write(TextsSQL)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 杂项：生成文件
def FilesMain():
    # 无需填充文本，直接生成文件
    ModifiersFile = FilePath + "\\" + fileName + "_Modifiers.sql"
    UnitAbilitiesFile = FilePath + "\\" + fileName + "_UnitAbilities.sql"
    ColorsFile = FilePath + "\\" + fileName + "_Colors.sql"

    SciptsFile = FilePath + "\\" + 'Scripts' + "\\" + fileName + "_Scripts.lua"
    UIluaFile = FilePath + "\\" + 'UI' + "\\" + fileName + "_UI.lua"
    UIxmlFile = FilePath + "\\" + 'UI' + "\\" + fileName + "_UI.xml"
    # 判断文件是否存在，不存在则创建
    with open(ModifiersFile, "w", encoding="utf-8") as f:
        f.write("")
    with open(UnitAbilitiesFile, "w", encoding="utf-8") as f:
        f.write("")
    with open(ColorsFile, "w", encoding="utf-8") as f:
        f.write("")

    # 创建Scripts文件夹
    ScriptsPath = FilePath + "\\" + 'Scripts'
    if not os.path.exists(ScriptsPath):
        os.makedirs(ScriptsPath)
    # 创建UI文件夹
    UIPath = FilePath + "\\" + 'UI'
    if not os.path.exists(UIPath):
        os.makedirs(UIPath)
    with open(SciptsFile, "w", encoding="utf-8") as f:
        f.write("")
    with open(UIluaFile, "w", encoding="utf-8") as f:
        f.write("")
    with open(UIxmlFile, "w", encoding="utf-8") as f:
        f.write(UIXml)

    MusicPath = FilePath + "\\" + 'Platforms' + "\\" + 'Windows' + "\\" + 'Audio'
    if not os.path.exists(MusicPath):
        os.makedirs(MusicPath)

    # Support文件夹
    SupportPath = FilePath + "\\" + 'Support'
    if not os.path.exists(SupportPath):
        os.makedirs(SupportPath)
    if SupportFile:
        # 直接从本目录复制Support.lua到Support文件夹
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'Support.lua'), SupportPath + "\\" + fileName + "_Support.lua")

    XLPsPath = FilePath + "\\" + 'XLPs'
    ArtDefsPath = FilePath + "\\" + 'ArtDefs'
    if not os.path.exists(XLPsPath):
        os.makedirs(XLPsPath)
    if not os.path.exists(ArtDefsPath):
        os.makedirs(ArtDefsPath)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

def XLP_BARBAROSSA(str):
    return f'''		<Element>
			<m_EntryID text="{str}_4"/>
			<m_ObjectName text="BARBAROSSA_4"/>
		</Element>'''

# XLPs文件
def XLPsMain():
    # 创建XLPs文件夹
    XLPsPath = FilePath + "\\" + 'XLPs'
    if not os.path.exists(XLPsPath):
        os.makedirs(XLPsPath)
    # 本地XLPs文件路径
    LocalXLPsFile = "XLPs\\"
    # 复制XLPs文件
    # SIQISIQISIQISIQI_dds.xlp，复制的同时，需要将SIQISIQISIQISIQI_dds替换为fileName + "_dds"，文件名和文件内容都要改
    ddsXLP = fileName + "_dds.xlp"
    shutil.copyfile(LocalXLPsFile + "SIQISIQISIQISIQI_dds.xlp", XLPsPath + "\\" + ddsXLP)
    # 读取文件内容，替换SIQISIQISIQISIQI_dds为fileName + "_dds"
    with open(XLPsPath + "\\" + ddsXLP, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("SIQISIQISIQISIQI_dds", fileName + "_dds")
    LeaderStr = ''
    if len(LeaderData) == 0:
        return
    LeadersData = Leaders(LeaderData)
    for leader in LeadersData.Leaders:
        LeaderStr += XLP_BARBAROSSA(Prefix + GetMidfix("领袖") + leader.ShortType) + '\n'
    content = content.replace("<m_Entries/>", f"<m_Entries>\n{LeaderStr}\t\t</m_Entries>")
    # 写回文件
    with open(XLPsPath + "\\" + ddsXLP, "w", encoding="utf-8") as f:
        f.write(content)
    #复制LeaderFallback.xlp，无需任何修改，直接复制
    shutil.copyfile(LocalXLPsFile + "LeaderFallback.xlp", XLPsPath + "\\" + "LeaderFallback.xlp")
    #复制tilebaseset.xlp，无需任何修改，直接复制
    shutil.copyfile(LocalXLPsFile + "tilebases.xlp", XLPsPath + "\\" + "tilebases.xlp")

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

def FindArtdefElement(xml_content):
    try:
        root = ET.fromstring(xml_content)
        second_level_elements = root.findall('.//m_RootCollections/Element/Element')
        return second_level_elements
    except etree.XMLSyntaxError as e:
        print(f"XML语法错误: {e}")
        return []
    
class ArtDefs:
    def __init__(self):
        self.Path = FilePath + "\\" + 'ArtDefs'
        self.LocalPath = "ArtDefs\\"
    def CivilizationArtDef(self):
        if len(CivData) == 0:
            return # 如果没有文明数据，直接返回
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Civilizations.artdef')
        Artdeffile = f"{self.Path}\\Civilizations.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        CivsData = Civs(CivData)
        Rows = []
        for civ in CivsData.Civs:
            Row = f'''        <Element>
            <m_CollectionName text="Civilization"/>
            <m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            <Element>
                <m_Fields>
                    <m_Values/>
                </m_Fields>
                <m_ChildCollections>
                    <Element>
                        <m_CollectionName text="Audio"/>
                        <m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
                    </Element>
                </m_ChildCollections>
                <m_Name text="{civ.Type}"/>
                <m_AppendMergedParameterCollections>false</m_AppendMergedParameterCollections>
            </Element>
        </Element>'''
            Rows.append(Row)
        NewContent = '\n'.join(Rows)
        with open(Artdeffile, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("</m_RootCollections>", f"{NewContent}\n</m_RootCollections>")
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(content)
    def CultureArtdef(self): # Cultures.artdef
        if len(CivData) == 0:
            return # 如果没有文明数据，直接返回
        # 直接复制即可
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Cultures.artdef')
        Artdeffile = f"{self.Path}\\Cultures.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
    def FallbackLeadersArtdef(self): # FallbackLeaders.artdef
        if len(LeaderData) == 0:
            return # 如果没有领袖数据，直接返回
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'FallbackLeaders.artdef')
        Artdeffile = f"{self.Path}\\FallbackLeaders.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        LeadersData = Leaders(LeaderData)
        Rows = []
        for leader in LeadersData.Leaders:
            Lead = leader.Type.replace('LEADER_', '')
            LeadImp = 'FALLBACK_NEUTRAL_' + Lead
            Row = f'''			<Element>
				<m_Fields>
					<m_Values/>
				</m_Fields>
				<m_ChildCollections>
					<Element>
						<m_CollectionName text="Animations"/>
						<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
						<Element>
							<m_Fields>
								<m_Values>
									<Element class="AssetObjects..BLPEntryValue">
										<m_EntryName text="{LeadImp}"/>
										<m_XLPClass text="LeaderFallback"/>
										<m_XLPPath text="leaderfallback.xlp"/>
										<m_BLPPackage text="LeaderFallbacks"/>
										<m_LibraryName text="LeaderFallback"/>
										<m_ParamName text="BLP Entry"/>
									</Element>
								</m_Values>
							</m_Fields>
							<m_ChildCollections/>
							<m_Name text="DEFAULT"/>
							<m_AppendMergedParameterCollections>false</m_AppendMergedParameterCollections>
						</Element>
					</Element>
				</m_ChildCollections>
				<m_Name text="{leader.Type}"/>
				<m_AppendMergedParameterCollections>false</m_AppendMergedParameterCollections>
			</Element>'''
            Rows.append(Row)
        NewContent = '\n'.join(Rows)
        content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..ArtDefSet>
	<m_Version>
		<major>1</major>
		<minor>0</minor>
		<build>0</build>
		<revision>0</revision>
	</m_Version>
	<m_TemplateName text="LeaderFallback"/>
	<m_RootCollections>
		<Element>
			<m_CollectionName text="Leaders"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            {NewContent}
		</Element>
	</m_RootCollections>
</AssetObjects..ArtDefSet>''' 
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(content)
    def FindDistrictArtdef(self, DistrictType, filexml):
        Elements = FindArtdefElement(filexml)
        for el in Elements:
            name = el.findall('.//m_Name')[-1].get('text')
            if name == DistrictType:
                return ET.tostring(el, encoding='utf-8').decode('utf-8')
        return False
    def DistrictArtdef(self): # Districts.artdef
        if len(DistrictData) == 0:
            return # 如果没有区域数据，直接返回
        DistrictsData = Districts(DistrictData)
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Districts.artdef')
        Artdeffile = f"{self.Path}\\Districts.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        # 文件路径
        ArtdefBaseFrom = os.path.join(os.path.dirname(__file__), 'From', 'Base', 'Districts.artdef')
        ArtdefDLCFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Districts.artdef')
        ArtdefDLCShareFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Districts_Shared.artdef')
        # 读取文件
        with open(ArtdefBaseFrom, "r", encoding="utf-8") as f:
            BaseContent = f.read()
        with open(ArtdefDLCFrom, "r", encoding="utf-8") as f:
            DLCContent = f.read()
        with open(ArtdefDLCShareFrom, "r", encoding="utf-8") as f:
            ShareContent = f.read()
        Rows = []
        BaseDistricts = []
        for district in DistrictsData.Districts:
            FromType = district.FromArtdef
            if FromType != 0:
                FromElement = self.FindDistrictArtdef(FromType, BaseContent)
                if FromElement:
                    BaseDistricts.append(district.Type)
                    NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{district.Type}"/>')
                    Rows.append(NewElement)
                else:
                    FromElement = self.FindDistrictArtdef(FromType, DLCContent)
                    if FromElement:
                        BaseDistricts.append(district.Type)
                        NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{district.Type}"/>')
                        Rows.append(NewElement)
                    else:
                        FromElement = self.FindDistrictArtdef(FromType, ShareContent)
                        if FromElement:
                            BaseDistricts.append(district.Type)
                            NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{district.Type}"/>')
                            Rows.append(NewElement)
                        else:
                            print(f"未找到区域 {district.Type} 的来源区域 {FromType}！")
            # 如果没有找到来源区域，则不进行复制
        if len(Rows) == 0:
            return
        NewContent = '\n'.join(Rows)
        Content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..ArtDefSet>
	<m_Version>
		<major>1</major>
		<minor>0</minor>
		<build>0</build>
		<revision>0</revision>
	</m_Version>
	<m_TemplateName text="Districts"/>
	<m_RootCollections>
		<Element>
			<m_CollectionName text="District"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            {NewContent}
		</Element>
		<Element>
			<m_CollectionName text="BuildStates"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
	</m_RootCollections>
</AssetObjects..ArtDefSet>'''
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(Content)
    def BuildingArtdef(self): # Buildings.artdef
        if len(BuildingData) == 0:
            return # 如果没有建筑数据，直接返回
        BuildingsData = Buildings(BuildingData)
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Buildings.artdef')
        Artdeffile = f"{self.Path}\\Buildings.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        # 文件路径
        ArtdefBaseFrom = os.path.join(os.path.dirname(__file__), 'From', 'Base', 'Buildings.artdef')
        ArtdefDLCFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Buildings.artdef')
        ArtdefDLCShareFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Buildings_Shared.artdef')
        # 读取文件
        with open(ArtdefBaseFrom, "r", encoding="utf-8") as f:
            BaseContent = f.read()
        with open(ArtdefDLCFrom, "r", encoding="utf-8") as f:
            DLCContent = f.read()
        with open(ArtdefDLCShareFrom, "r", encoding="utf-8") as f:
            ShareContent = f.read()
        Rows = []
        BaseBuildings = []
        for building in BuildingsData.Buildings:
            FromType = building.FromArtdef
            if FromType != 0:
                FromElement = self.FindDistrictArtdef(FromType, BaseContent)
                if FromElement:
                    BaseBuildings.append(building.Type)
                    NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{building.Type}"/>')
                    Rows.append(NewElement)
                else:
                    FromElement = self.FindDistrictArtdef(FromType, DLCContent)
                    if FromElement:
                        BaseBuildings.append(building.Type)
                        NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{building.Type}"/>')
                        Rows.append(NewElement)
                    else:
                        FromElement = self.FindDistrictArtdef(FromType, ShareContent)
                        if FromElement:
                            BaseBuildings.append(building.Type)
                            NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{building.Type}"/>')
                            Rows.append(NewElement)
                        else:
                            print(f"未找到建筑 {building.Type} 的来源建筑 {FromType}！")
        if len(Rows) == 0:
            return
        NewContent = '\n'.join(Rows)
        Content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..ArtDefSet>
	<m_Version>
		<major>1</major>
		<minor>0</minor>
		<build>0</build>
		<revision>0</revision>
	</m_Version>
	<m_TemplateName text="Buildings"/>
	<m_RootCollections>
		<Element>
			<m_CollectionName text="Building"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            {NewContent}
		</Element>
		<Element>
			<m_CollectionName text="BuildStates"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="BuildingChains"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
	</m_RootCollections>
</AssetObjects..ArtDefSet>'''
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(Content)
    def UnitArtdef(self): # Units.artdef
        if len(UnitData) == 0:
            return # 如果没有单位数据，直接返回
        UnitsData = Units(UnitData)
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Units.artdef')
        Artdeffile = f"{self.Path}\\Units.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        # 文件路径
        ArtdefBaseFrom = os.path.join(os.path.dirname(__file__), 'From', 'Base', 'Units.artdef')
        ArtdefDLCFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Units.artdef')
        # 读取文件
        with open(ArtdefBaseFrom, "r", encoding="utf-8") as f:
            BaseContent = f.read()
        with open(ArtdefDLCFrom, "r", encoding="utf-8") as f:
            DLCContent = f.read()
        Rows = []
        BaseUnits = []
        for unit in UnitsData.Units:
            FromType = unit.FromArtdef
            if FromType != 0:
                FromElement = self.FindDistrictArtdef(FromType, BaseContent)
                if FromElement:
                    BaseUnits.append(unit.Type)
                    NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{unit.Type}"/>')
                    Rows.append(NewElement)
                else:
                    FromElement = self.FindDistrictArtdef(FromType, DLCContent)
                    if FromElement:
                        BaseUnits.append(unit.Type)
                        NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{unit.Type}"/>')
                        Rows.append(NewElement)
                    else:
                        print(f"未找到单位 {unit.Type} 的来源单位 {FromType}！")
        if len(Rows) == 0:
            return
        NewContent = '\n'.join(Rows)
        Content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..ArtDefSet>
	<m_Version>
		<major>1</major>
		<minor>0</minor>
		<build>0</build>
		<revision>0</revision>
	</m_Version>
	<m_TemplateName text="Units"/>
	<m_RootCollections>
		<Element>
			<m_CollectionName text="Units"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            {NewContent}
		</Element>
		<Element>
			<m_CollectionName text="UnitMovementTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitFormationTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="MemberCombat"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitCombat"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="CombatAttack"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitFormationLayoutTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="CombatFormation"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitDomainTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitAttachmentBins"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitMemberTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitTintTypes"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
		<Element>
			<m_CollectionName text="UnitGlobals"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
	</m_RootCollections>
</AssetObjects..ArtDefSet>'''
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(Content)
    def ImprovementArtdef(self): # Improvements.artdef
        if len(ImprovementData) == 0:
            return # 如果没有改良设施数据，直接返回
        ImprovementsData = Improvements(ImprovementData)
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Improvements.artdef')
        Artdeffile = f"{self.Path}\\Improvements.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)
        # 文件路径
        ArtdefBaseFrom = os.path.join(os.path.dirname(__file__), 'From', 'Base', 'Improvements.artdef')
        ArtdefDLCFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Improvements.artdef')
        ArtdefDLCShareFrom = os.path.join(os.path.dirname(__file__), 'From', 'DLC', 'Improvements_Shared.artdef')
        # 读取文件
        with open(ArtdefBaseFrom, "r", encoding="utf-8") as f:
            BaseContent = f.read()
        with open(ArtdefDLCFrom, "r", encoding="utf-8") as f:
            DLCContent = f.read()
        with open(ArtdefDLCShareFrom, "r", encoding="utf-8") as f:
            ShareContent = f.read()
        Rows = []
        BaseImprovements = []
        for improvement in ImprovementsData.Improvements:
            FromType = improvement.FromArtdef
            if FromType != 0:
                FromElement = self.FindDistrictArtdef(FromType, BaseContent)
                if FromElement:
                    BaseImprovements.append(improvement.Type)
                    NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{improvement.Type}"/>')
                    Rows.append(NewElement)
                else:
                    FromElement = self.FindDistrictArtdef(FromType, DLCContent)
                    if FromElement:
                        BaseImprovements.append(improvement.Type)
                        NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{improvement.Type}"/>')
                        Rows.append(NewElement)
                    else:
                        FromElement = self.FindDistrictArtdef(FromType, ShareContent)
                        if FromElement:
                            BaseImprovements.append(improvement.Type)
                            NewElement = FromElement.replace(f'<m_Name text="{FromType}" />', f'<m_Name text="{improvement.Type}"/>')
                            Rows.append(NewElement)
                        else:
                            print(f"未找到改良设施 {improvement.Type} 的来源改良设施 {FromType}！")
        if len(Rows) == 0:
            return
        NewContent = '\n'.join(Rows)
        Content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..ArtDefSet>
	<m_Version>
		<major>1</major>
		<minor>0</minor>
		<build>0</build>
		<revision>0</revision>
	</m_Version>
	<m_TemplateName text="Improvements"/>
	<m_RootCollections>
		<Element>
			<m_CollectionName text="Improvement"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
            {NewContent}
		</Element>
		<Element>
			<m_CollectionName text="BuildStates"/>
			<m_ReplaceMergedCollectionElements>false</m_ReplaceMergedCollectionElements>
		</Element>
	</m_RootCollections>
</AssetObjects..ArtDefSet>'''
        with open(Artdeffile, "w", encoding="utf-8") as f:
            f.write(Content)
    def LandmarksArtdef(self):
        # 纯复制，只要Districts.artdef或Buildings.artdef或Improvements.artdef存在，就复制Landmarks.artdef
        if len(DistrictData) == 0 and len(BuildingData) == 0 and len(ImprovementData) == 0:
            return # 如果没有区域、建筑、改良设施数据，直接返回
        ArtdefTemplate = os.path.join(os.path.dirname(__file__), 'Artdefs', 'Landmarks.artdef')
        Artdeffile = f"{self.Path}\\Landmarks.artdef"
        shutil.copy(ArtdefTemplate, Artdeffile)


# Artdefs文件
def ArtDefsMain():
    # 创建ArtDefs文件夹
    ArtDefsPath = FilePath + "\\" + 'ArtDefs'
    if not os.path.exists(ArtDefsPath):
        os.makedirs(ArtDefsPath)
    artdefs = ArtDefs()
    artdefs.CivilizationArtDef()
    artdefs.CultureArtdef()
    artdefs.FallbackLeadersArtdef()
    artdefs.DistrictArtdef()
    artdefs.BuildingArtdef()
    artdefs.UnitArtdef()
    artdefs.ImprovementArtdef()
    artdefs.LandmarksArtdef()

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 一级文件名根
FilesRoot = ['_Civilizations.sql', '_Leaders.sql', '_Districts.sql', '_Buildings.sql', '_Units.sql', '_Improvements.sql', '_Governors.sql', '_Projects.sql', '_Policies.sql', '_Moments.sql', '_Modifiers.sql', '_UnitAbilities.sql']
IconsRoot = ['_Icons.xml']
ColorRoot = ['_Colors.sql']
# 文本文件根
TextRoot = ['_Texts_CN.sql', '_Texts_EN.sql', '_Texts_HK.sql']
# Scripts文件根
ScriptRoot = ['_Scripts.lua']
# UI文件根
UIRoot = ['_UI']

# 工程文件
def Civ6ProjectFile(Guid, ProjectGuid,str1,str2):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="12.0" DefaultTargets="Default" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Default</Configuration>
    <Name>{fileName}</Name>
    <Guid>{Guid}</Guid>
    <ProjectGuid>{ProjectGuid}</ProjectGuid>
    <ModVersion>1</ModVersion>
    <Teaser>{fileName}</Teaser>
    <Description>{fileName}</Description>
    <Authors>{Authors}</Authors>
    <SpecialThanks>
    </SpecialThanks>
    <AffectsSavedGames>true</AffectsSavedGames>
    <SupportsSinglePlayer>true</SupportsSinglePlayer>
    <SupportsMultiplayer>true</SupportsMultiplayer>
    <SupportsHotSeat>true</SupportsHotSeat>
    <CompatibleVersions>1.2,2.0</CompatibleVersions>
    <AssociationData><![CDATA[<Associations><Dependency type="Dlc" title="Expansion: Rise and Fall" id="1B28771A-C749-434B-9053-D1380C553DE9" /></Associations>]]></AssociationData>
    {str1}
    <AssemblyName>{fileName}</AssemblyName>
    <RootNamespace>{fileName}</RootNamespace>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)' == 'Default' ">
    <OutputPath>.</OutputPath>
  </PropertyGroup>
  <ItemGroup>
    <None Include="{fileName}.Art.xml" />
  </ItemGroup>
  {str2}
  <Import Project="$(MSBuildLocalExtensionPath)Civ6.targets" />
</Project>'''

# 判断文件是否存在
def HasFile(file):
    path = FilePath + "\\" + file
    return os.path.exists(path)

# 配置文件主函数
def ModinfoMain():
    filepath = FilePath + "\\" + fileName + ".civ6proj"
    # 判断文件是否存在
    if not os.path.exists(filepath):
        # 报错
        raise ValueError(f"未找到配置文件 {filepath}，请先生成文明文件或领袖文件！")
    # 读取文件
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # 从文件中提取Guid和ProjectGuid
    Gird = re.search(r"<Guid>(.*?)</Guid>", content).group(1)
    ProjectGuid = re.search(r"<ProjectGuid>(.*?)</ProjectGuid>", content).group(1)
    def GetContent(str):
        return f'''    <Content Include="{str}">
      <SubType>Content</SubType>
    </Content>'''
    # 生成配置文件
    Contents = [] # 导入的文件
    LoadOrder = f"<Properties><LoadOrder>{LoadOrderNumber}</LoadOrder></Properties>" # 加载顺序
    UpdateDatabasef = f'<UpdateDatabase id="UpdateDatabase"><File>{fileName}_Configs.sql</File></UpdateDatabase>'
    Contents.append(GetContent(f"{fileName}_Configs.sql"))
    UpdateDatabaseg = '<UpdateDatabase id="UpdateDatabase">'
    if LoadOrderNumber != 0:
        UpdateDatabaseg += LoadOrder
    for root in FilesRoot:
        if HasFile(fileName + root):
            Contents.append(GetContent(fileName + root))
            UpdateDatabaseg += f'<File>{fileName}{root}</File>'
    UpdateDatabaseg += '</UpdateDatabase>'

    TextPath = "\\Text"
    UpdateText = f'<UpdateText id="UpdateText">'
    for root in TextRoot:
        if HasFile(f"{TextPath}\\{fileName}{root}"):
            Contents.append(GetContent(f"Text\\{fileName}{root}"))
            UpdateText += f'<File>Text/{fileName}{root}</File>'
    UpdateText += '</UpdateText>'

    UpdateIcons = f'<UpdateIcons id="UpdateIcons">'
    for root in IconsRoot:
        if HasFile(f"{fileName}{root}"):
            Contents.append(GetContent(f"{fileName}{root}"))
            UpdateIcons += f'<File>{fileName}{root}</File>'
    UpdateIcons += '</UpdateIcons>'

    UpdateColors = f'<UpdateColors id="UpdateColors">'
    Has = False
    for root in ColorRoot:
        if HasFile(f"{fileName}{root}"):
            Contents.append(GetContent(f"{fileName}{root}"))
            UpdateColors += f'<File>{fileName}{root}</File>'
            Has = True
    UpdateColors += '</UpdateColors>'
    if not Has:
        UpdateColors = '' # 如果没有颜色文件，则不添加该节点

    ScriptsPath = "\\Scripts"
    AddGameplayScripts = f'<AddGameplayScripts id="AddGameplayScripts">'
    Has = False
    for root in ScriptRoot:
        if HasFile(f"{ScriptsPath}\\{fileName}{root}"):
            Contents.append(GetContent(f"Scripts\\{fileName}{root}"))
            AddGameplayScripts += f'<File>Scripts/{fileName}{root}</File>'
            Has = True
    AddGameplayScripts += '</AddGameplayScripts>'
    if not Has:
        AddGameplayScripts = '' # 如果没有脚本文件，则不添加该节点

    UIPath = "\\UI"
    AddUIScripts = f'<AddUserInterfaces id="AddUserInterfaces"><Properties><Context>InGame</Context></Properties>'
    Has = False
    for root in UIRoot:
        if HasFile(f"{UIPath}\\{fileName}{root}.xml"):
            Contents.append(GetContent(f"UI\\{fileName}{root}.xml"))
            Contents.append(GetContent(f"UI\\{fileName}{root}.lua"))
            AddUIScripts += f'<File>UI/{fileName}{root}.xml</File>'
            Has = True
    AddUIScripts += '</AddUserInterfaces>'
    if not Has:
        AddUIScripts = '' # 如果没有UI文件，则不添加该节点

    SupportPath = "\\Support"
    AddSupport = f'<ImportFiles id="ImportFiles">'
    Has = False
    if HasFile(f"{SupportPath}\\{fileName}_Support.lua"):
        Contents.append(GetContent(f"Support\\{fileName}_Support.lua"))
        AddSupport += f'<File>Support/{fileName}_Support.lua</File>'
        Has = True
    AddSupport += '</ImportFiles>'
    if not Has:
        AddSupport = '' # 如果没有Support文件，则不添加该节点

    FrontEndActionData = f'''<FrontEndActionData><![CDATA[<FrontEndActions>{UpdateDatabasef}{UpdateText}{UpdateIcons}{UpdateColors}<UpdateArt id="UpdateArt"><File>(Mod Art Dependency File)</File></UpdateArt></FrontEndActions>]]></FrontEndActionData>'''
    InGameActionData = f'''<InGameActionData><![CDATA[<InGameActions>{UpdateColors}{UpdateText}{UpdateIcons}<UpdateArt id="UpdateArt"><File>(Mod Art Dependency File)</File></UpdateArt>{AddGameplayScripts}{AddUIScripts}{AddSupport}{UpdateDatabaseg}</InGameActions>]]></InGameActionData>'''

    ContentStr = "\n".join(Contents)
    Newcontent = f'''<ItemGroup>\n{ContentStr}</ItemGroup>\n<ItemGroup>
    <Folder Include="Platforms\\" />
    <Folder Include="Platforms\\Windows\\" />
    <Folder Include="Platforms\\Windows\\Audio\\" />
    <Folder Include="Scripts\\" />
    <Folder Include="Support\\" />
    <Folder Include="Text\\" />
    <Folder Include="UI\\" />
  </ItemGroup>'''
    
    content = Civ6ProjectFile(Gird, ProjectGuid, FrontEndActionData + "\n    " + InGameActionData, Newcontent)
    # 写回文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ======================================================================================================================================================================
# ======================================================================================================================================================================
# ======================================================================================================================================================================

# 总的主函数
def main():
    start_time = time.time()
    print("Mod工具开始运行...")
    # 文件夹是否存在
    if not os.path.exists(FilePath):
        # 报错
        raise ValueError(f"未找到文件夹 {FilePath}，请检查路径是否正确！")
    # 生成文明文件
    CivMain()
    print("文明文件生成完毕！")
    # 生成领袖文件
    LeaderMain()
    print("领袖文件生成完毕！")
    # 生成Config文件
    ConfigMain()
    print("Config文件生成完毕！")
    # 生成Icon文件
    IconMain()
    print("Icon文件生成完毕！")
    # 生成区域文件
    DistrictMain()
    print("区域文件生成完毕！")
    # 生成建筑文件
    BuildingMain()
    print("建筑文件生成完毕！")
    # 生成单位文件
    UnitMain()
    print("单位文件生成完毕！")
    # 生成改良设施文件
    ImprovementMain()
    print("改良设施文件生成完毕！")
    # 生成总督文件
    GovernorMain()
    print("总督文件生成完毕！")
    # 生成项目文件
    ProjectMain()
    print("项目文件生成完毕！")
    # 生成政策卡文件
    PolicyMain()
    print("政策卡文件生成完毕！")
    # 生成历史时刻文件
    HistoricalMomentMain()
    print("历史时刻文件生成完毕！")
    # 生成文本文件
    TextMain()
    print("文本文件生成完毕！")
    # 生成杂项文件
    FilesMain()
    print("杂项文件生成完毕！")
    # 生成XLPs文件
    XLPsMain()
    print("XLPs文件生成完毕！")
    # 生成ArtDefs文件
    ArtDefsMain()
    print("ArtDefs文件生成完毕！")
    # 生成配置文件
    ModinfoMain()
    print("配置文件生成完毕！")
    # 结束
    end_time = time.time()
    print(f"Mod工具运行完毕！总共用时 {end_time - start_time:.2f} 秒。")

if __name__ == "__main__":
    if not StopMain:
        main()


