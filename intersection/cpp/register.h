#include <string>
#include <vector>

class CellRegistry
{
public:
    struct Item
    {
        std::string id;
        int row;
        int col;
        bool IsValid() const { return row >= 0; }
    };
    struct KeyVal
    {
        int time;
        std::vector<Item> items;
        bool IsValid() const { return time >= 0; }
    };

    CellRegistry();

    void SetTime(int time);
    void Register(int time, const char* id, int row, int col);
    void UnregisterAll(const char* id);
    char* GetRegisteredId(int time, int row, int col);
    bool IsRegistered(int time, int row, int col);
    
private:
    KeyVal& GetKeyVal(int time);
    Item& FindItem(int time, int row, int col);
    Item& FindItem(KeyVal& keyVal, int row, int col);
    KeyVal& FindKeyVal(int time);

private:
    int currentIdx_ = 0;
    std::vector<KeyVal> data_;
};