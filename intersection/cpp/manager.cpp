#include "manager.h"

#include <iostream>

extern "C" 
{

Manager* Man_new() {
    Manager* man = new Manager();
    return man;
}

void Man_delete(Manager* man) {
    delete man; 
}

bool Man_is_cell_registered(Manager* man, int time, int row, int col)
{
    return man->IsCellRegistered(time, row, col);
}

bool Man_can_register(Manager* man, PyObject* lane, float laneLength, float carLength, float carWidth, int beginTime, int endTime)
{
    man->CanRegister(lane, laneLength, carLength, carWidth, beginTime, endTime);
}

void Man_register(Manager* man, PyObject* lane, float laneLength, float carLength, float carWidth, const char* carID, int beginTime, int endTime)
{
    man->Register(lane, laneLength, carLength, carWidth, std::string(carID), beginTime, endTime);
}

void Man_unregister(Manager* man, const char* carID)
{
    man->Unregister(std::string(carID));
}

void Man_set_time(Manager* man, int time)
{
    man->SetTime(time);
}


} // extern "C"

static std::vector<Cell> GetCells(PyObject* lane, int distance)
{
    if (!Py_IsInitialized())
        Py_Initialize();
    auto gstate = PyGILState_Ensure();

    PyObject* get_cells = PyObject_GetAttrString(lane, "get_cells_");
    PyObject* args = Py_BuildValue("(i)", distance);
    PyObject* res = PyEval_CallObject(get_cells, args);
    Py_DECREF(get_cells);
    Py_DECREF(args);
    std::vector<int> values;
    if (!res)
        return {};
    if (PyList_Check(res)) {
        for (Py_ssize_t i = 0; i < PyList_Size(res); ++i) {
            PyObject* next = PyList_GetItem(res, i);
            if (next) {
                int val = 0;
                PyArg_Parse(next, "i", &val);
                values.push_back(val);
            }
        }
    }
    Py_DECREF(res);
    PyGILState_Release(gstate);
    std::vector<Cell> cells;
    for (int i = 0; i < values.size(); i += 2) {
        Cell cell;
        cell.col = values[i];
        cell.row = values[i + 1];
        cells.push_back(cell);
    }
    return cells;
}

Manager::Manager()
{

}

void Manager::ForEachStep(PyObject* lane, float laneLength, 
        float carLength, float carWidth, int beginTime, int endTime,
        const std::function<bool(int /*time*/, const Cell&)>& callback)
{
    int timeCount = endTime - beginTime;
    float length = laneLength + carLength;
    float distanceStep = length / timeCount;
    for (int t = 0; t < timeCount; ++t) {
        float d = t * distanceStep;
        std::vector<Cell> cells = GetCells(lane, d);
        for (Cell cell : cells) {
            if (!callback(t, cell))
                return;
        }
    }
}

bool Manager::CanRegister(PyObject* lane, float laneLength, 
        float carLength, float carWidth, int beginTime, int endTime)
{
    bool canRegister = true;
    ForEachStep(lane, laneLength, carLength, carWidth, beginTime, endTime,
            [&, this] (int time, const Cell& cell) {
        if (registry_.IsRegistered(beginTime + time, cell.row, cell.col)) {
            canRegister = false;
            return false;
        }
        return true;
    });
    return canRegister;
}

void Manager::Register(PyObject* lane, float laneLength, 
        float carLength, float carWidth, const std::string& carID, int beginTime, int endTime)
{
    ForEachStep(lane, laneLength, carLength, carWidth, beginTime, endTime,
            [&, this] (int time, const Cell& cell) {
        registry_.Register(beginTime + time, carID.c_str(), cell.row, cell.col);
        return true;
    });
}

void Manager::Unregister(const std::string& carID)
{
    registry_.UnregisterAll(carID.c_str());
}

bool Manager::IsCellRegistered(int time, int row, int col)
{
    return registry_.IsRegistered(time, row, col);
}

void Manager::SetTime(int time)
{
    registry_.SetTime(time);
}