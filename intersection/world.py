from junction import Junction
from manager import Manager
from PyQt5.QtCore import *

import os, sys, warnings, logging

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(os.environ['SUMO_HOME'])
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib

def prev_next_iter(iterable):
    prev = None
    for curr in iterable:
        if prev:
            yield prev, curr
        prev = curr

class Route:
    def __init__(self, id):
        self.id = id
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_length(self):
        length = 0
        for edge in self.edges:
            length += edge.length
        for edge, next_edge in prev_next_iter(self.edges):
            junction = edge.to_junction
            lane = junction.get_lane(edge.id, next_edge.id)
            length += lane.length
        return length

    def get_next_junction(self, edge_id):
        length = 0
        for edge, next_edge in prev_next_iter(self.edges):
            length += edge.length
            junction = edge.to_junction
            lane = junction.get_lane(edge.id, next_edge.id)
            if edge.id == edge_id:
                return length, lane, junction
            length += lane.length
        # probably internal edge = lane
        return 0, None, None

    #not tested
    def get_next_junction_for_dist(self, distance):
        length = 0
        for edge, next_edge in prev_next_iter(self.edges):
            length += edge.length
            junction = edge.to_junction
            lane = junction.get_lane(edge.id, next_edge.id)
            if length > distance:
                return length, lane, junction
            length += lane.length
        # probably internal edge = lane
        return 0, None, None


def convert_shape(s):
    shape = []
    for x, y in s:
        shape.append(QPointF(x, y))
    return shape

class Edge:
    def __init__(self, id, from_junction, to_junction, length):
        self.id = id
        self.from_junction = from_junction
        self.to_junction = to_junction
        self.length = length

    def __repr__(self):
        return repr('Edge|' + str(self.id) +'| ' + self.from_junction.id + '->' + self.to_junction.id)


class World:
    def __init__(self):
        self.agents = {}

    def load_net(self, filename):
        self.junctions = {}
        self.edges = {}
        net = sumolib.net.readNet(filename, withInternal=True)

        mergelanes = {}
        for mergelane in sumolib.output.parse_fast(filename, 'mergelane', ['id', 'lanes']):
            for lane in mergelane.lanes.split():
                mergelanes.setdefault(mergelane.id, []).append(lane)

        for node in net.getNodes():
            shape = convert_shape(node.getShape())
            if not shape:
                continue
            junction = Junction(node.getID(), shape)
            self.junctions[node.getID()] = junction

        for e in net.getEdges(withInternal = False):
            from_junction = self.junctions[e.getFromNode().getID()]
            to_junction = self.junctions[e.getToNode().getID()]
            edge = Edge(e.getID(), from_junction, 
                        to_junction, e.getLength())
            self.edges[e.getID()] = edge

    
        for id_, junction in self.junctions.items():
            node = net.getNode(id_)
            connections = [c for c in node.getConnections() if c.getFrom().getID() in self.edges and c.getTo().getID() in self.edges]
            lanes = []
            for laneID in node.getInternal():
                if laneID:
                    lanes.append(laneID)

            for connection in connections:
                from_edge = self.edges.get(connection.getFrom().getID(), None)
                to_edge = self.edges.get(connection.getTo().getID(), None)
                lane = None
                laneShape = None
                laneLength = 0
                if connection.getViaLaneID() in lanes:
                    lane = net.getLane(connection.getViaLaneID())
                    laneShape = convert_shape(lane.getShape())
                    laneLength = lane.getLength()
                elif connection.getViaLaneID() in mergelanes:
                    mergelane = mergelanes[connection.getViaLaneID()]
                    lane_id = next((l for l in mergelane if l in lanes), None)
                    lane = net.getLane(lane_id)
                    laneLength = lane.getLength()
                    shape = net.getLane(connection.getViaLaneID()).getShape()
                    for lane_id in mergelane:
                        shape.extend(net.getLane(lane_id).getShape())
                        laneLength += net.getLane(lane_id).getLength()
                    laneShape = convert_shape(shape)

                if not lane or not laneShape:
                    continue
                junction.add_lane(lane.getID(), laneShape, laneLength, from_edge, to_edge)
            
            if lanes:
                junction.manager = Manager()
            else:
                del self.junctions[id_]


    def load_routes(self, filename):
        self.routes = {}
        for route in sumolib.output.parse_fast(filename, 'route', ['edges', 'id']):
            r = Route(route.id)
            for edge_id in route.edges.split():
                if edge_id not in self.edges:
                    logging.warning("Edge not found " + str(edge_id))
                    continue
                edge = self.edges[edge_id]
                r.add_edge(edge)
            self.routes[r.id] = r
