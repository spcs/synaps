/*
 Copyright (c) 2012 Samsung SDS Co., LTD
 All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
 */

package com.spcs.synaps;

import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.spout.ShellSpout;
import backtype.storm.task.ShellBolt;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.IRichSpout;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.tuple.Fields;
import backtype.storm.utils.Utils;

import java.util.Map;
import java.util.Properties;

public class PutMetricTopology {
	public static class ApiSpout extends ShellSpout implements IRichSpout {
		public ApiSpout() {
			super("python", "-u", "synstorm_api_spout.py");
		}

		@Override
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("message"));
		}

		@Override
		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	public static class CheckSpout extends ShellSpout implements IRichSpout {
		public CheckSpout() {
			super("python", "-u", "synstorm_check_spout.py");
		}

		@Override
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("metric_key", "message"));
		}

		@Override
		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	public static class UnpackMessageBolt extends ShellBolt implements
			IRichBolt {
		public UnpackMessageBolt() {
			super("python", "-u", "synstorm_unpack_bolt.py");
		}

		@Override
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("metric_key", "message"));
		}

		@Override
		public Map<String, Object> getComponentConfiguration() {
			return null;
		}

	}

	public static class PutMetricBolt extends ShellBolt implements IRichBolt {
		public PutMetricBolt() {
			super("python", "-u", "synstorm_put_metric_bolt.py");
		}

		@Override
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("alarm_key", "message"));
		}

		@Override
		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	public static class ActionBolt extends ShellBolt implements IRichBolt {
		public ActionBolt() {
			super("python", "-u", "synstorm_action_bolt.py");
		}

		@Override
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
		}

		@Override
		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		TopologyBuilder builder = new TopologyBuilder();
		// Properties properties = new Properties();
		//
		// properties.load(PutMetricTopology.class
		// .getResourceAsStream("synapsstorm.properties"));
		//
		// String topology_name = properties.getProperty("topology_name");
		// int n_workers =
		// Integer.parseInt(properties.getProperty("n_workers"));
		// int n_api_spout = Integer.parseInt(properties
		// .getProperty("n_api_spout"));
		// int n_check_spout = Integer.parseInt(properties
		// .getProperty("n_check_spout"));
		// int n_unpack_bolt = Integer.parseInt(properties
		// .getProperty("n_unpack_bolt"));
		// int n_putmetric_bolt = Integer.parseInt(properties
		// .getProperty("n_putmetric_bolt"));
		// int n_action_bolt = Integer.parseInt(properties
		// .getProperty("n_action_bolt"));

		Config conf = new Config();
		conf.setDebug(true);

		if (args != null && args.length > 0) {
			conf.setNumWorkers(20);
			conf.setNumAckers(20);
			conf.setMaxSpoutPending(500);
			builder.setSpout("api_spout", new ApiSpout(), 8);
			builder.setSpout("check_spout", new CheckSpout(), 1);
			builder.setBolt("unpack_bolt", new UnpackMessageBolt(), 8)
					.shuffleGrouping("api_spout");
			builder.setBolt("putmetric_bolt", new PutMetricBolt(), 20)
					.fieldsGrouping("unpack_bolt", new Fields("metric_key"))
					.allGrouping("check_spout");
			builder.setBolt("action_bolt", new ActionBolt(), 2)
					.shuffleGrouping("putmetric_bolt");
			StormSubmitter.submitTopology("synaps" + args[0], conf,
					builder.createTopology());
		} else {
			builder.setSpout("api_spout", new ApiSpout(), 2);
			builder.setSpout("check_spout", new CheckSpout(), 1);
			builder.setBolt("unpack_bolt", new UnpackMessageBolt(), 2)
					.shuffleGrouping("api_spout");
			builder.setBolt("putmetric_bolt", new PutMetricBolt(), 4)
					.fieldsGrouping("unpack_bolt", new Fields("metric_key"))
					.allGrouping("check_spout");
			builder.setBolt("action_bolt", new ActionBolt(), 2)
					.shuffleGrouping("putmetric_bolt");
			LocalCluster cluster = new LocalCluster();
			cluster.submitTopology("metric", conf, builder.createTopology());
			Utils.sleep(30 * 60 * 1000); // 30 min
			cluster.killTopology("metric");
			Utils.sleep(10 * 1000); // 10 sec
			cluster.shutdown();
		}
	}
}
