# Copyright 2015 Balazs Sonkoly, Janos Czentye
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Abstract class and implementation for basic operations with a single NF-FG, such
as building, parsing, processing NF-FG, helper functions, etc.
"""
import copy
from pprint import pprint

import networkx
from networkx.exception import NetworkXError

from nffg_elements import *


class AbstractNFFG(object):
  """
  Abstract class for managing single NF-FG data structure.

  The NF-FG data model is described in YANG. This class provides the
  interfaces with the high level data manipulation functions.
  """

  # NFFG specific functions

  def add_nf (self):
    """
    Add a single NF node to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_sap (self):
    """
    Add a single SAP node to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_infra (self):
    """
    Add a single infrastructure node to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_link (self, src, dst):
    """
    Add a static or dynamic infrastructure link to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_sglink (self, src, dst):
    """
    Add an SG link to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_req (self, src, dst):
    """
    Add a requirement link to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_node (self, node):
    """
    Add a single node to the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def del_node (self, id):
    """
    Remove a single node from the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  def add_edge (self, src, dst, link):
    """
    Add an edge to the NF-FG..
    """
    raise NotImplementedError("Not implemented yet!")

  def del_edge (self, src, dst):
    """
    Remove an edge from the NF-FG.
    """
    raise NotImplementedError("Not implemented yet!")

  # General functions for create/parse/dump/convert NFFG

  @classmethod
  def parse (cls, data):
    """
    General function for parsing data as a new :any::`NFFG` object and return
    with its reference.

    :param data: raw data
    :type data: str
    :return: parsed NFFG as an XML object
    :rtype: Virtualizer
    """
    raise NotImplementedError("Not implemented yet!")

  def dump (self):
    """
    General function for dumping :any::`NFFG` according to its format to
    plain text.

    :return: plain text representation
    :rtype: str
    """
    raise NotImplementedError("Not implemented yet!")


class NFFG(AbstractNFFG):
  """
  Internal NFFG representation based on networkx.
  """
  # Some pre-define constant to avoid NFFGModel related class imports
  DOMAIN_INTERNAL = NodeInfra.DOMAIN_INTERNAL
  DOMAIN_VIRTUAL = NodeInfra.DOMAIN_VIRTUAL
  DOMAIN_OS = NodeInfra.DOMAIN_OS
  DOMAIN_UN = NodeInfra.DOMAIN_UN
  DOMAIN_DOCKER = NodeInfra.DOMAIN_DOCKER
  TYPE_INFRA_SW = NodeInfra.TYPE_SDN_SWITCH
  TYPE_INFRA_EE = NodeInfra.TYPE_EE
  TYPE_INFRA_STATIC_EE = NodeInfra.TYPE_STATIC_EE
  TYPE_INFRA_BISBIS = NodeInfra.TYPE_BISBIS

  def __init__ (self, id=None, name=None, version="1.0"):
    """
    Init

    :param id: optional NF-FG identifier (generated by default)
    :type id: str or int
    :param name: optional NF-FG name (generated by default)
    :type name: str
    :param version: optional version (default: 1.0)
    :type version: str
    :return: None
    """
    super(NFFG, self).__init__()
    self.network = networkx.MultiDiGraph()
    self.id = str(id) if id is not None else str(generate(self))
    self.name = name if name is not None else "NFFG-" + str(self.id)
    self.version = version

  @property
  def nfs (self):
    return (node for id, node in self.network.nodes_iter(data=True) if
            node.type == Node.NF)

  @property
  def saps (self):
    return (node for id, node in self.network.nodes_iter(data=True) if
            node.type == Node.SAP)

  @property
  def infras (self):
    return (node for id, node in self.network.nodes_iter(data=True) if
            node.type == Node.INFRA)

  @property
  def links (self):
    return (link for src, dst, link in self.network.edges_iter(data=True) if
            link.type == Link.STATIC or link.type == Link.DYNAMIC)

  @property
  def sg_hops (self):
    return (link for s, d, link in self.network.edges_iter(data=True) if
            link.type == Link.SG)

  @property
  def reqs (self):
    return (link for s, d, link in self.network.edges_iter(data=True) if
            link.type == Link.REQUIREMENT)

  def __str__ (self):
    return "NFFG(id=%s name=%s, version=%s)" % (
      self.id, self.name, self.version)

  def __repr__ (self):
    return super(NFFG, self).__repr__()

  ##############################################################################
  # Builder design pattern related functions
  ##############################################################################

  def add_node (self, node):
    """
    Add a Node to the structure.

    :param node: a Node object
    :type node: :any:`Node`
    :return: None
    """
    self.network.add_node(node.id)
    self.network.node[node.id] = node

  def del_node (self, node):
    """
    Remove the node from the structure.

    :param node: node id or node object or a port object of the node
    :type node: str or :any:`Node` or :any`Port`
    :return: the actual node is found and removed or not
    :rtype: bool
    """
    try:
      if isinstance(node, Node):
        node = node.id
      elif isinstance(node, Port):
        node = node.node.id
      self.network.remove_node(node)
      return True
    except NetworkXError:
      # There was no node in the graph
      pass

  def add_edge (self, src, dst, link):
    """
    Add an Edge to the structure.

    :param src: source node id or Node object or a Port object
    :type src: str or :any:`Node` or :any`Port`
    :param dst: destination node id or Node object or a Port object
    :type dst: str or :any:`Node` or :any`Port`
    :param link: edge data object
    :type link: :any:`Link`
    :return: None
    """
    if isinstance(src, Node):
      src = src.id
    elif isinstance(src, Port):
      src = src.node.id
    if isinstance(dst, Node):
      dst = dst.id
    elif isinstance(dst, Port):
      dst = dst.node.id
    self.network.add_edge(src, dst, key=link.id)
    self.network[src][dst][link.id] = link

  def del_edge (self, src, dst, id=None):
    """
    Remove the edge(s) between two nodes.

    :param src: source node id or Node object or a Port object
    :type src: str or :any:`Node` or :any`Port`
    :param dst: destination node id or Node object or a Port object
    :type dst: str or :any:`Node` or :any`Port`
    :param id: unique id of the edge (otherwise remove all)
    :type id: str or int
    :return: the actual node is found and removed or not
    :rtype: bool
    """
    try:
      if isinstance(src, Node):
        src = src.id
      elif isinstance(src, Port):
        src = src.node.id
      if isinstance(dst, Node):
        dst = dst.id
      elif isinstance(dst, Port):
        dst = dst.node.id
      if id is not None:
        self.network.remove_edge(src, dst, key=id)
      else:
        self.network[src][dst].clear()
      return True
    except NetworkXError:
      # There was no node in the graph
      pass

  def add_nf (self, id=None, name=None, func_type=None, dep_type=None, cpu=None,
       mem=None, storage=None, delay=None, bandwidth=None):
    """
    Add a Network Function to the structure.

    :param id: optional id
    :type id: str or int
    :param name: optional name
    :type name: str
    :param func_type: functional type (default: "None")
    :type func_type: str
    :param dep_type: deployment type (default: "None")
    :type dep_type: str
    :param cpu: CPU resource
    :type cpu: str or int
    :param mem: memory resource
    :type mem: str or int
    :param storage: storage resource
    :type storage: str or int
    :param delay: delay property of the Node
    :type delay: float
    :param bandwidth: bandwidth property of the Node
    :type bandwidth: float
    :return: newly created node
    :rtype: :any:`NodeNF`
    """
    res = NodeResource(cpu=cpu, mem=mem, storage=storage, delay=delay,
                       bandwidth=bandwidth) if any(
      i is not None for i in (cpu, mem, storage, delay, bandwidth)) else None
    nf = NodeNF(id=id, name=name, func_type=func_type, dep_type=dep_type,
                res=res)
    self.add_node(nf)
    return nf

  def add_sap (self, id=None, name=None):
    """
    Add a Service Access Point to the structure.

    :param id: optional id
    :type id: str or int
    :param name: optional name
    :type name: str
    :return: newly created node
    :rtype: :any:`NodeSAP`
    """
    sap = NodeSAP(id=id, name=name)
    self.add_node(sap)
    return sap

  def add_infra (self, id=None, name=None, domain=None, infra_type=None,
       cpu=None, mem=None, storage=None, delay=None, bandwidth=None):
    """
    Add an Infrastructure Node to the structure.

    :param id: optional id
    :type id: str or int
    :param name: optional name
    :type name: str
    :param domain: domain of the Infrastructure Node (default: None)
    :type domain: str
    :param infra_type: type of the Infrastructure Node (default: 0)
    :type infra_type: int or str
    :param cpu: CPU resource
    :type cpu: str or int
    :param mem: memory resource
    :type mem: str or int
    :param storage: storage resource
    :type storage: str or int
    :param delay: delay property of the Node
    :type delay: float
    :param bandwidth: bandwidth property of the Node
    :type bandwidth: float
    :return: newly created node
    :rtype: :any:`NodeInfra`
    """
    res = NodeResource(cpu=cpu, mem=mem, storage=storage, bandwidth=bandwidth,
                       delay=delay) if any(
      i is not None for i in (cpu, mem, storage, delay, bandwidth)) else None
    infra = NodeInfra(id=id, name=name, domain=domain, infra_type=infra_type,
                      res=res)
    self.add_node(infra)
    return infra

  def add_link (self, src_port, dst_port, id=None, dynamic=False,
       backward=False, delay=None, bandwidth=None):
    """
    Add a Link to the structure.

    :param src_port: source Node
    :type src_port: :any:`Port`
    :param dst_port: destination port
    :type dst_port: :any:`Port`
    :param id: optional link id
    :type id: str or int
    :param delay: delay resource
    :type delay: str or int
    :param dynamic: set the link dynamic (default: False)
    :type dynamic: bool
    :param bandwidth: bandwidth resource
    :type bandwidth: str or int
    :return: newly created edge
    :rtype: :any:`EdgeLink`
    """
    type = Link.DYNAMIC if dynamic else Link.STATIC
    link = EdgeLink(src=src_port, dst=dst_port, type=type, id=id,
                    backward=backward, delay=delay, bandwidth=bandwidth)
    self.add_edge(src_port.node, dst_port.node, link)
    return link

  def add_undirected_link (self, port1, port2, p1p2id=None, p2p1id=None,
       dynamic=False, delay=None, bandwidth=None):
    """
    Add two Links to the structure, in both directions.

    :param port1: source port
    :type port1: :any:`Port`
    :param port2: destination port
    :type port2: :any:`Port`
    :param p1p2id: optional link id from port1 to port2
    :type p1p2id: str or int
    :param p2p1id: optional link id from port2 to port1
    :type p2p1id: str or int
    :param delay: delay resource of both links
    :type delay: str or int
    :param dynamic: set the link dynamic (default: False)
    :type dynamic: bool
    :param bandwidth: bandwidth resource of both links
    :type bandwidth: str or int
    :return: newly created edge tuple in (p1->p2, p2->p1)
    :rtype: :any:(`EdgeLink`, `EdgeLink`)
    """
    linkp1p2 = self.add_link(port1, port2, id=p1p2id, dynamic=dynamic,
                             backward=False, delay=delay, bandwidth=bandwidth)
    linkp2p1 = self.add_link(port2, port1, id=p2p1id, dynamic=dynamic,
                             backward=True, delay=delay, bandwidth=bandwidth)
    return linkp1p2, linkp2p1

  def add_sglink (self, src_port, dst_port, id=None, flowclass=None):
    """
    Add a SD next hop edge to the structure.

    :param src_port: source Node
    :type src_port: :any:`Port`
    :param dst_port: destination port
    :type dst_port: :any:`Port`
    :param id: optional link id
    :type id: str or int
    :param flowclass: flowclass of SG next hop link
    :type flowclass: str
    :return: newly created edge
    :rtype: :any:`EdgeSGLink`
    """
    hop = EdgeSGLink(src=src_port, dst=dst_port, id=id, flowclass=flowclass)
    self.add_edge(src_port.node, dst_port.node, hop)
    return hop

  def add_req (self, src_port, dst_port, id=None, delay=None, bandwidth=None):
    """
    Add a requirement edge to the structure.

    :param src_port: source Node
    :type src_port: :any:`Port`
    :param dst_port: destination port
    :type dst_port: :any:`Port`
    :param id: optional link id
    :type id: str or int
    :param delay: delay resource
    :type delay: str or int
    :param bandwidth: bandwidth resource
    :type bandwidth: str or int
    :return: newly created edge
    :rtype: :any:`EdgeReq`
    """
    req = EdgeReq(src=src_port, dst=dst_port, id=id, delay=delay,
                  bandwidth=bandwidth)
    self.add_edge(src_port.node, dst_port.node, req)
    return req

  def dump (self):
    """
    Convert the NF-FG structure to a NFFGModel format and return the plain
    text representation.

    :return: text representation
    :rtype: str
    """
    # Create the model
    nffg = NFFGModel(id=self.id, name=self.name, version=self.version)
    # Load Infras
    for infra in self.infras:
      nffg.node_infras.append(infra)
    # Load SAPs
    for sap in self.saps:
      nffg.node_saps.append(sap)
    # Load NFs
    for nf in self.nfs:
      nffg.node_nfs.append(nf)
    # Load Links
    for link in self.links:
      nffg.edge_links.append(link)
    # Load SG next hops
    for hop in self.sg_hops:
      nffg.edge_sg_nexthops.append(hop)
    # Load Requirements
    for req in self.reqs:
      nffg.edge_reqs.append(req)
    # Dump
    return nffg.dump()

  @classmethod
  def parse (cls, raw_data):
    """
    Read the given JSON object structure and try to convert to an NF-FG
    representation as an :any:`NFFG`

    :param raw_data: raw NF-FG description as a string
    :type raw_data: str
    :return: the parsed NF-FG representation
    :rtype: :any:`NFFG`
    """
    # Parse text
    model = NFFGModel.parse(raw_data)
    # Create new NFFG
    nffg = NFFG(id=model.id, name=model.name, version=model.version)
    # Load Infras
    for infra in model.node_infras:
      nffg.add_node(infra)
    # Load SAPs
    for sap in model.node_saps:
      nffg.add_node(sap)
    # Load NFs
    for nf in model.node_nfs:
      nffg.add_node(nf)
    # Load Links
    for link in model.edge_links:
      nffg.add_edge(link.src.node, link.dst.node, link)
    # Load SG next hops
    for hop in model.edge_sg_nexthops:
      nffg.add_edge(hop.src.node, hop.dst.node, hop)
    # Load Requirements
    for req in model.edge_reqs:
      nffg.add_edge(req.src.node, req.dst.node, req)
    return nffg

  ##############################################################################
  # Helper functions
  ##############################################################################

  def duplicate_static_links (self):
    """
    Extend the NFFG model with backward links for STATIC links to fit for the
    orchestration algorithm.

    STATIC links: infra-infra, infra-sap

    :return: None
    """
    # Create backward links
    backwards = [
      EdgeLink(src=link.dst, dst=link.src, id=link.id + "-back", backward=True,
               delay=link.delay, bandwidth=link.bandwidth) for u, v, link in
      self.network.edges_iter(data=True) if link.type == Link.STATIC]
    # Add backward links to the NetworkX structure in a separate step to
    # avoid the link reduplication caused by the iterator based for loop
    for link in backwards:
      self.add_edge(src=link.src, dst=link.dst, link=link)

  def merge_duplicated_links (self):
    """
    Detect duplicated STATIC links which both are connected to the same
    Port/Node and have switched source/destination direction to fit for the
    simplified NFFG dumping.

    Only leaves one of the links, but that's not defined which one.

    :return: None
    """
    # Collect backward links
    backwards = [(src, dst, key) for src, dst, key, link in
                 self.network.edges_iter(keys=True, data=True) if
                 link.type == Link.STATIC and link.backward is True]
    # Delete backwards links
    for link in backwards:
      self.network.remove_edge(*link)

  def infra_neighbors (self, infra_id):
    """
    Return an iterator for the Infra nodes which are neighbours of the given
    node.

    :param infra_id: infra node
    :type infra_id: :any:`NodeInfra`
    :return: iterator for the list of Infra nodes
    """
    return {self.network.node[id] for id in
            self.network.neighbors_iter(infra_id) if
            self.network.node[id].type == Node.INFRA}

  def running_nfs (self, infra_id):
    """
    Return an iterator for the NodeNFs which are mapped to the given Infra node.

    :params infra_id: infra node identifier
    :type infra_id: :any: `NodeInfra`
    :return: iterator for the currently running NodeNFs
    """
    return {self.network.node[id] for id in
            self.network.neighbors_iter(infra_id) if
            self.network.node[id].type == Node.NF}

  def copy (self):
    """
    Return the deep copy of the NFFG object.

    :return: deep copy
    :rtype: :any:`NFFG`
    """
    copy = NFFG(id=self.id, name=self.name, version=self.version)
    copy.network = self.network.copy()
    return copy

  def generate_id (self):
    """
    Generate a unique id from object memory address.

    :return: generated id
    :rtype: str
    """
    self.id = str(generate(self))
    return self.id


def test_NFFG ():
  # Add nodes
  nffg = NFFG(id="BME-001")
  infra = nffg.add_infra(id="node0", name="INFRA0")
  sap0 = nffg.add_sap(id="SAP1")
  sap1 = nffg.add_sap(id="SAP2")
  nf1 = nffg.add_nf(id="NF1", name="NetFunc1")
  nf2 = nffg.add_nf(id="NF2", name="NetFunc2")
  nf3 = nffg.add_nf(id="NF3", name="NetFunc3")
  # Add ports and edges
  nffg.add_link(sap0.add_port(1), infra.add_port(0), id="infra_in")
  nffg.add_link(sap1.add_port(1), infra.add_port(1), id="infra_out")
  nffg.add_link(infra.add_port(2), nf1.add_port(1), id="nf1_in", dynamic=True)
  nffg.add_link(nf1.add_port(2), infra.add_port(3), id="nf1_out", dynamic=True)
  nffg.add_link(infra.add_port(4), nf2.add_port(1), id="nf2_in", dynamic=True)
  nffg.add_link(nf2.add_port(2), infra.add_port(5), id="nf2_out", dynamic=True)
  nffg.add_link(infra.add_port(6), nf3.add_port(1), id="nf3_in", dynamic=True)
  nffg.add_link(nf3.add_port(2), infra.add_port(7), id="nf3_out", dynamic=True)
  # Add SG hops
  nffg.add_sglink(sap0.ports[1], nf1.ports[1], id="hop1")
  nffg.add_sglink(nf1.ports[2], nf2.ports[1], id="hop2")
  nffg.add_sglink(nf2.ports[2], nf3.ports[1], id="hop3")
  nffg.add_sglink(nf3.ports[1], sap1.ports[1], id="hop4")
  nffg.add_sglink(sap1.ports[1], sap0.ports[1], id="hop_back")
  # Add req
  nffg.add_req(sap0.ports[1], sap1.ports[1], id="req", delay=10, bandwidth=100)
  # Dump NetworkX structure
  print "\nNetworkX:"
  pprint(nffg.network.__dict__)
  # Dump NFFGModel structure
  print "\nNFFGModel:"
  nffg_dump = nffg.dump()
  print nffg_dump
  # Dump tests
  print "\nNFs:"
  for nf in nffg.nfs:
    print nf
  print "\nSG next hops:"
  for hop in nffg.sg_hops:
    print hop

  # Parse NFFG
  print "\nParsed NF-FG:"
  print NFFG.parse(nffg_dump).dump()

  # Copy test

  print "Copied NF-FG:"
  # pprint(nffg.copy().network.__dict__)
  pprint(copy.deepcopy(nffg).network.__dict__)


def generate_mn_topo ():
  # Create NFFG
  nffg = NFFG(id="INTERNAL", name="Internal-Mininet-Topology")
  # Add environments
  # TODO - define supported types (that's only need to the orchestration)
  ee1 = nffg.add_infra(id="EE1", name="ee-infra-1", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_EE, cpu=0, mem=0, storage=0,
                       delay=0, bandwidth=0)
  ee2 = nffg.add_infra(id="EE2", name="ee-infra-2", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_EE, cpu=0, mem=0, storage=0,
                       delay=0, bandwidth=0)
  # Add OVS switches
  sw3 = nffg.add_infra(id="SW3", name="switch-3", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_SDN_SWITCH)
  sw4 = nffg.add_infra(id="SW4", name="switch-4", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_SDN_SWITCH)
  # Add SAPs
  sap1 = nffg.add_sap(id="SAP1", name="SAP1")
  sap2 = nffg.add_sap(id="SAP2", name="SAP2")
  # Add links
  nffg.add_link(ee1.add_port(1), sw3.add_port(1), id="link1")
  nffg.add_link(ee2.add_port(1), sw4.add_port(1), id="link2")
  nffg.add_link(sw3.add_port(2), sw4.add_port(2), id="link3")
  nffg.add_link(sw3.add_port(3), sap1.add_port(1), id="link4")
  nffg.add_link(sw4.add_port(3), sap2.add_port(1), id="link5")
  nffg.duplicate_static_links()
  pprint(nffg.network.__dict__)
  nffg.merge_duplicated_links()
  txt = nffg.dump()
  print txt
  # parsed = NFFG.parse(txt)
  # print parsed.dump()
  return nffg


def generate_dynamic_fallback_nffg ():
  nffg = NFFG(id="DYNAMIC-FALLBACK-TOPO", name="fallback-dynamic")
  nc1 = nffg.add_infra(id="nc1", name="NC1", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_EE, cpu=5, mem=5, storage=5,
                       delay=0.9, bandwidth=5000)
  nc2 = nffg.add_infra(id="nc2", name="NC2", domain=NFFG.DOMAIN_INTERNAL,
                       infra_type=NodeInfra.TYPE_EE, cpu=5, mem=5, storage=5,
                       delay=0.9, bandwidth=5000)
  nc1.add_supported_type(['A','B'])
  nc2.add_supported_type(['A','C'])
  s3 = nffg.add_infra(id="s3", name="S3", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH,
                      delay=0.2, bandwidth=10000)
  s4 = nffg.add_infra(id="s4", name="S4", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH,
                      delay=0.2, bandwidth=10000)
  sap1 = nffg.add_sap(id="sap1", name="SAP1")
  sap2 = nffg.add_sap(id="sap2", name="SAP2")
  linkres = {'delay': 1.5, 'bandwidth': 2000}
  nffg.add_link(nc1.add_port(1), s3.add_port(1), id="l1", **linkres)
  nffg.add_link(nc2.add_port(1), s4.add_port(1), id="l2", **linkres)
  nffg.add_link(s3.add_port(2), s4.add_port(2), id="l3", **linkres)
  nffg.add_link(s3.add_port(3), sap1.add_port(1), id="l4", **linkres)
  nffg.add_link(s4.add_port(3), sap2.add_port(1), id="l5", **linkres)
  nffg.duplicate_static_links()
  # pprint(nffg.network.__dict__)
  # nffg.merge_duplicated_links()
  # print nffg.dump()
  return nffg


def generate_static_fallback_topo ():
  nffg = NFFG(id="STATIC-FALLBACK-TOPO", name="fallback-static")
  s1 = nffg.add_infra(id="s1", name="S1", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH)
  s2 = nffg.add_infra(id="s2", name="S2", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH)
  s3 = nffg.add_infra(id="s3", name="S3", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH)
  s4 = nffg.add_infra(id="s4", name="S4", domain=NFFG.DOMAIN_INTERNAL,
                      infra_type=NodeInfra.TYPE_SDN_SWITCH)
  sap1 = nffg.add_sap(id="sap1", name="SAP1")
  sap2 = nffg.add_sap(id="sap2", name="SAP2")
  nffg.add_link(s1.add_port(1), s3.add_port(1), id="l1")
  nffg.add_link(s2.add_port(1), s4.add_port(1), id="l2")
  nffg.add_link(s3.add_port(2), s4.add_port(2), id="l3")
  nffg.add_link(s3.add_port(3), sap1.add_port(1), id="l4")
  nffg.add_link(s4.add_port(3), sap2.add_port(1), id="l5")
  nffg.duplicate_static_links()
  pprint(nffg.network.__dict__)
  nffg.merge_duplicated_links()
  print nffg.dump()
  return nffg


if __name__ == "__main__":
  # test_NFFG()
  generate_mn_topo()
  # generate_dynamic_fallback_nffg()
  # generate_static_fallback_topo()
