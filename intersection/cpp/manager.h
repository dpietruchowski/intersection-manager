#include "register.h"

#include <Python.h>
#include <functional>

struct Cell
{
    int row;
    int col;
};

class Manager
{
public:
    Manager();

    bool IsCellRegistered(int time, int row, int col);
    bool CanRegister(PyObject* lane, float laneLength, float carLength, float carWidth, int beginTime, int endTime);
    void Register(PyObject* lane, float laneLength, float carLength, float carWidth, const std::string& carID, int beginTime, int endTime);
    void Unregister(const std::string& carID);
    void SetTime(int time);

private:
    void ForEachStep(PyObject* lane, float laneLength, float carLength, float carWidth, int beginTime, int endTime,
                    const std::function<bool(int /*time*/, const Cell&)>& callback);

private:
    CellRegistry registry_;
};