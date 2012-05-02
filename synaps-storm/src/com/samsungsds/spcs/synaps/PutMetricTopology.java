package com.samsungsds.spcs.synaps;

import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.spout.ShellSpout;
import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.OutputCollector;
import backtype.storm.task.ShellBolt;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.IRichSpout;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;
import backtype.storm.utils.Utils;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class PutMetricTopology {
	public static class ApiSpout extends ShellSpout implements IRichSpout {
		public ApiSpout() {
			super("python", "api_spout.py");
		}

		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("message"));
		}

		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	public static class UnpackMessageBolt extends ShellBolt implements
			IRichBolt {
		public UnpackMessageBolt() {
			super("python", "unpack_message_bolt.py");
		}

		public void declareOutputFields(OutputFieldsDeclarer declarer) {
			declarer.declare(new Fields("metric_id", "message"));
		}

		public Map<String, Object> getComponentConfiguration() {
			return null;
		}

	}

	public static class PutMetricBolt extends ShellBolt implements IRichBolt {
		public PutMetricBolt() {
			super("python", "put_metric_bolt.py");
		}

		public void declareOutputFields(OutputFieldsDeclarer declarer) {
		}

		public Map<String, Object> getComponentConfiguration() {
			return null;
		}
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		TopologyBuilder builder = new TopologyBuilder();

		builder.setSpout("api_spout", new ApiSpout(), 2);
		builder.setBolt("unpack_message_bolt", new UnpackMessageBolt(), 2)
				.shuffleGrouping("api_spout");
		builder.setBolt("putmetric_bolt", new PutMetricBolt(), 2)
				.fieldsGrouping("unpack_message_bolt", new Fields("metric_id"));

		Config conf = new Config();
		conf.setDebug(true);

		if (args != null && args.length > 0) {
			conf.setNumWorkers(3);
			StormSubmitter.submitTopology(args[0], conf,
					builder.createTopology());
		} else {
			LocalCluster cluster = new LocalCluster();
			cluster.submitTopology("test", conf, builder.createTopology());
			Utils.sleep(10000);
			cluster.killTopology("test");
			Utils.sleep(10000);
			cluster.shutdown();
		}
	}
}