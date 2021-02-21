#include "register.h"

#include <algorithm>
#include <iostream>
#include <string.h>

extern "C" 
{

CellRegistry* Reg_new() {
    CellRegistry* reg = new CellRegistry();
    return reg;
}

void Reg_delete(CellRegistry* reg) {
    delete reg; 
}

void Reg_set_time(CellRegistry* reg, int time) {
    reg->SetTime(time);
}

void Reg_register(CellRegistry* reg, int time, const char* id, int row, int col) {
    reg->Register(time, id, row, col);
}

void Reg_unregister_all(CellRegistry* reg, const char* id) {
    reg->UnregisterAll(id);
}

char* Reg_get_registered_id(CellRegistry* reg, int time, int row, int col) {
    char* ptr = reg->GetRegisteredId(time, row, col);
    return ptr;
}

void Reg_free(char* ptr) {
    free(ptr);
}

} // extern "C"

CellRegistry::CellRegistry(): data_()
{

}

void CellRegistry::SetTime(int time)
{
    if (data_.size() == 0 || data_[currentIdx_].time < time)
        return;
    std::sort(data_.begin(), data_.end(), [](KeyVal& k1, KeyVal& k2) {
        return k1.time < k2.time;   
    });
    currentIdx_ = 0;/*
    for(int i = 0; i < data_.size(); ++i) {
        KeyVal& keyVal = data_[i];
        std::cout << keyVal.time << std::endl;
    }*/
    for(int i = 0; i < data_.size(); ++i) {
        KeyVal& keyVal = data_[i];
        if (keyVal.time > time) {
            currentIdx_ = i;
            break;
        }
    }
    currentIdx_ = std::min(currentIdx_, static_cast<int>(data_.size()) - 1);
    currentIdx_ = std::max(currentIdx_, 0);
}

void CellRegistry::Register(int time, const char* id, int row, int col)
{
    KeyVal& keyVal = GetKeyVal(time);
    Item& item = FindItem(keyVal, row, col);
    if (item.IsValid()) {
        return;
    }
    std::string id_(id);
    keyVal.items.push_back(Item{id, row, col});
    /*
    for(KeyVal& keyVal : data_) {
        std::cout << keyVal.time << std::endl;
        for(Item& item: keyVal.items) {
            std::cout << "   " << item.id << " " << item.col << " " << item.row << std::endl;
        }
    }*/
}

void CellRegistry::UnregisterAll(const char* id)
{
    std::string id_(id);
    for(KeyVal& keyVal : data_) {
        auto begin = std::begin(keyVal.items);
        auto end = std::end(keyVal.items);
        keyVal.items.erase(std::remove_if(begin, end,
            [&id_](const Item& item) {
                return item.id == id_;
        }), end);
    }
}

char* CellRegistry::GetRegisteredId(int time, int row, int col)
{
    Item item = FindItem(time, row, col);
    if (!item.IsValid())
        return nullptr;
    return strdup(item.id.c_str());
}

bool CellRegistry::IsRegistered(int time, int row, int col)
{
    Item item = FindItem(time, row, col);
    if (!item.IsValid())
        return false;
    return true;
}

CellRegistry::KeyVal& CellRegistry::GetKeyVal(int time)
{
    KeyVal& keyVal = FindKeyVal(time);
    if (keyVal.IsValid()) {
        return keyVal;
    }
    data_.push_back(KeyVal{time, {}});
    return data_.back();
}

CellRegistry::Item& CellRegistry::FindItem(int time, int row, int col)
{
    KeyVal& keyVal = FindKeyVal(time);
    if (!keyVal.IsValid()) {
        static Item none = {"", -1, -1 };
        return none;
    }
    return FindItem(keyVal, row, col);
}
    
CellRegistry::Item& CellRegistry::FindItem(CellRegistry::KeyVal& keyVal, int row, int col)
{
    for(Item& item: keyVal.items) {
        if (item.row == row && item.col == col) {
            return item;
        }
    }
    static Item none = {"", -1, -1 };
    return none;
}

CellRegistry::KeyVal& CellRegistry::FindKeyVal(int time)
{
    for(int i = currentIdx_; i < data_.size(); ++i) {
        KeyVal& keyVal = data_[i];
        if (keyVal.time == time)
            return keyVal;
    }
    static KeyVal none = {-1, {}};
    return none;
}
