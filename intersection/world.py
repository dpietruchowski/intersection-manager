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

def prevNextIter(iterable):
    prev = None
    for curr in iterable:
        if prev:
            yield prev, curr
        prev = curr

class Route:
    def __init__(self, id):
        self.id = id
        self.edges = []

    def addEdge(self, edge):
        self.edges.append(edge)

    def getLength(self):
        length = 0
        for edge in self.edges:
            length += edge.length
        for edge, nextEdge in prevNextIter(self.edges):
            junction = edge.toJunction
            lane = junction.getLane(edge.id, nextEdge.id)
            length += lane.length
        return length

    def getNextJunction(self, edgeId):
        length = 0
        for edge, nextEdge in prevNextIter(self.edges):
            length += edge.length
            junction = edge.toJunction
            lane = junction.getLane(edge.id, nextEdge.id)
            if edge.id == edgeId:
                return length, lane, junction
            length += lane.length
        # probably internal edge = lane
        return 0, None, None


def convertShape(s):
    shape = []
    for x, y in s:
        shape.append(QPointF(x, y))
    return shape

class Edge:
    def __init__(self, id, fromJunction, toJunction, length):
        self.id = id
        self.fromJunction = fromJunction
        self.toJunction = toJunction
        self.length = length

    def __repr__(self):
        return repr('Edge|' + str(self.id) +'| ' + self.fromJunction.id + '->' + self.toJunction.id)


class World:
    def loadNet(self, filename):
        self.junctions = {}
        self.edges = {}
        net = sumolib.net.readNet(filename, withInternal=True)

        for node in net.getNodes():
            shape = convertShape(node.getShape())
            if not shape:
                continue
            junction = Junction(node.getID(), shape)
            self.junctions[node.getID()] = junction

        for e in net.getEdges(withInternal = False):
            fromJunction = self.junctions[e.getFromNode().getID()]
            toJunction = self.junctions[e.getToNode().getID()]
            edge = Edge(e.getID(), fromJunction, 
                        toJunction, e.getLength())
            self.edges[e.getID()] = edge
            
        for node in net.getNodes():
            junction = self.junctions[node.getID()]
            if not junction:
                logging.warning("Junction not found " + str(node.getID()))
                continue

            lanes = []
            for laneID in node.getInternal():
                if laneID:
                    lanes.append(laneID)

            for laneID in lanes:
                connection = None
                for conn in node.getConnections():
                    if conn.getViaLaneID() == laneID:
                        connection = conn
                        break
                if not connection:
                    logging.warning("Connection not found for lane " + str(laneID))
                    continue
                
                lane = net.getLane(laneID)
                laneShape = convertShape(lane.getShape())
                fromEdge = None
                if connection.getFrom().getID() in self.edges:
                    fromEdge = self.edges[connection.getFrom().getID()]
                toEdge = None
                if connection.getTo().getID() in self.edges:
                    toEdge = self.edges[connection.getTo().getID()]
                junction.addLane(laneID, laneShape, lane.getLength(), fromEdge, toEdge)
            
            if lanes:
                junction.manager = Manager()


    def loadRoutes(self, filename):
        self.routes = {}
        for route in sumolib.output.parse_fast(filename, 'route', ['edges', 'id']):
            print route
            r = Route(route.id)
            for edgeId in route.edges.split():
                if edgeId not in self.edges:
                    logging.warning("Edge not found " + str(edgeId))
                    continue
                edge = self.edges[edgeId]
                r.addEdge(edge)
            self.routes[r.id] = r
