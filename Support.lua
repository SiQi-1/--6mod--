
SiqiGP = {}
SiqiUI = {}

-- 玩家判断函数
function SiqiGP.IsCivilization(playerID, civilizationType)
    local pPlayerConfig = PlayerConfigurations[playerID]
    if pPlayerConfig == nil then return false; end
    if pPlayerConfig:GetCivilizationTypeName() == civilizationType then return true;
    else return false; end
end

function SiqiGP.IsLeader(playerID, leaderType)
    local pPlayerConfig = PlayerConfigurations[playerID]
    if pPlayerConfig == nil then return false; end
    if pPlayerConfig:GetLeaderTypeName() == leaderType then return true;
    else return false; end
end

function SiqiGP.HasTrait(playerID, sTrait)
    if playerID == nil or sTrait== nil then return false; end --首先，获取玩家配置
    local playerConfig = PlayerConfigurations[playerID]
    if playerConfig == nil then return false; end --然后，获取玩家的文明和领袖类型
    local sCiv = playerConfig:GetCivilizationTypeName()
    local sLea = playerConfig:GetLeaderTypeName()
    for tRow in GameInfo.CivilizationTraits() do
        if (tRow.CivilizationType == sCiv and tRow.TraitType == sTrait) then return true; end
    end
    for tRow in GameInfo.LeaderTraits() do
        if (tRow.LeaderType == sLea and tRow.TraitType == sTrait) then return true; end
    end
    return false;
end

function SiqiGP.HasProperty(pOdject, sProperty)
    if not pOdject then return false; end
    local property = pOdject:GetProperty(sProperty)
    if not property or property <= 0 then return false; end
    return true
end

-- 产出修改函数
function SiqiGP.ChangeScience(playerID, amount)
    local player = Players[playerID]
    pPlayer:GetTechs():ChangeCurrentResearchProgress(amount)
end

function SiqiGP.ChangeCulture(playerID, amount)
    local player = Players[playerID]
    pPlayer:GetCulture():ChangeCurrentCulturalProgress(amount)
end

function SiqiGP.ChangeGold(playerID, amount)
    local player = Players[playerID]
    pPlayer:GetTreasury():ChangeGoldBalance(amount)
end

function SiqiGP.ChangeFaith(playerID, amount)
    local player = Players[playerID]
    pPlayer:GetReligion():ChangeFaithBalance(amount)
end

function SiqiGP.ChangeProduction(playerID, amount, cityID)
    local player = Players[playerID]
    if not cityID then
        local pCities = player:GetCities()
        for _, pCity in pCities:Members() do
            pCity:GetBuildQueue():AddProgress(amount)
        end
        return
    end
    local pCity = CityManager.GetCity(playerID, cityID)
    if pCity then
        pCity:GetBuildQueue():AddProgress(amount)
    end
end

-- 单位类
function SiqiGP.ChangeUnitDamage(playerID, unitID, amount)
    local pUnit = UnitManager.GetUnit(playerID, unitID)
    if pUnit == nil then return; end
    local MaxDamage = pUnit:GetMaxDamage()
    local unitdamage = pUnit:GetDamage()
    if unitdamage + damage >= MaxDamage then
        UnitManager.Kill(pUnit, true)
    else
        pUnit:ChangeDamage(damage)
    end
end

-- 文本类
function SiqiGP.GetYieldString(YieldType)
    if not GameInfo.Yields[YieldType] then return ""; end
    return GameInfo.Yields[YieldType].IconString..Locale.Lookup(GameInfo.Yields[YieldType].Name)
end

-- 快捷映射
SiqiGP["CIVILIZATION"] = SiqiGP.IsCivilization
SiqiGP["LEADER"] = SiqiGP.IsLeader
SiqiGP["TRAIT"] = SiqiGP.HasTrait
SiqiGP["PROPERTY"] = SiqiGP.HasProperty
SiqiUI["CIVILIZATION"] = SiqiGP.IsCivilization
SiqiUI["LEADER"] = SiqiGP.IsLeader
SiqiUI["TRAIT"] = SiqiGP.HasTrait
SiqiUI["PROPERTY"] = SiqiGP.HasProperty

SiqiGP["YIELD_SCIENCE"] = SiqiGP.ChangeScience
SiqiGP["YIELD_CULTURE"] = SiqiGP.ChangeCulture
SiqiGP["YIELD_GOLD"] = SiqiGP.ChangeGold
SiqiGP["YIELD_FAITH"] = SiqiGP.ChangeFaith
SiqiGP["YIELD_PRODUCTION"] = SiqiGP.ChangeProduction

SiqiGP["UNIT_DAMAGE"] = SiqiGP.ChangeUnitDamage

SiqiGP["YIELD_STRING"] = SiqiGP.GetYieldString
SiqiUI["YIELD_STRING"] = SiqiGP.GetYieldString












