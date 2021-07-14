#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.


from cortx.utils.log import Log
from ha.alert.alert_monitor import AlertMonitor
from ha.alert.iem import IemGenerator
from ha.execute import SimpleCommand

class NodeAlertMonitor(AlertMonitor):

    def __init__(self):
        """
        Init node alert monitor
        """
        super(NodeAlertMonitor, self).__init__()

    def process_alert(self):
        Log.debug("Processing event for NodeAlertMonitor")
        # Environment variable are avilable in self.crm_env
        self.iem = IemGenerator()
        alert_dup = AlertDuplication()
        self.node_ids, self.local_node = alert_dup.AlertDuplication().get_status()

        if self.node_ids[-1] == self.local_node:
            self.iem.generate_iem(self.crm_env["CRM_alert_node"], self.alert_event_module, self.alert_event_type)
            Log.info(f"Sent IEM alert from local node: {self.local_node}")
        else:
            Log.info(f"Not the highest node to sent IEM node failure alert.")

class AlertDuplication:
    """
    Alert duplication.
    """
    def __init__(self):
        """
        Init method.
        """
        self.process = SimpleCommand()
    
    def get_status(self):
        self._nodeids, self._err, self._rc = self.process.run_cmd("pcs status corosync | awk '{print $1}' | tail -n+5")
        self._local_node, self._err, self._rc = self.process.run_cmd("crm_node -i")
        Log.info(f"List of online node ids in cluster: {self._nodeids.split()}")
        Log.info(f"Local node id: {self._local_node}")
        self.nodeids_list = self._nodeids.split() 
        self.sort_nodeids(self.nodeids_list, self._local_node)

    def sort_nodeids(self, nodeids_list: list, local_node):
        """
        Sort node ids in ascending order.
        """
        self.nodeids_list = nodeids_list
        self.local_node = local_node
        self.nodeids_list.sort()
        Log.info(f"Sorted node ids: {self.nodeids_list}")
        return self.nodeids_list.sort(), self.local_node