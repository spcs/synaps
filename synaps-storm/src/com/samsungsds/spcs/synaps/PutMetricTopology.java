package com.samsungsds.spcs.synaps;

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

public class PutMetricTopology {
	public static class ApiSpout extends ShellSpout implements IRichSpout {
		public ApiSpout() {
			super("python", "api_spout.py");
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

	public static class UnpackMessageBolt extends ShellBolt implements
			IRichBolt {
		public UnpackMessageBolt() {
			super("python", "unpack_message_bolt.py");
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
			super("python", "put_metric_bolt.py");
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

		builder.setSpout("api_spout", new ApiSpout(), 2);
		builder.setBolt("unpack_bolt", new UnpackMessageBolt(), 5)
		.shuffleGrouping("api_spout");
		builder.setBolt("putmetric_bolt", new PutMetricBolt(), 10)
				.fieldsGrouping("unpack_bolt", new Fields("metric_key"));

		Config conf = new Config();
		conf.setDebug(true);

		if (args != null && args.length > 0) {
			conf.setNumWorkers(6);
			StormSubmitter.submitTopology(args[0], conf,
					builder.createTopology());
		} else {
			LocalCluster cluster = new LocalCluster();
			cluster.submitTopology("metric", conf, builder.createTopology());
			Utils.sleep(10000);
			cluster.killTopology("metric");
			Utils.sleep(10000);
			cluster.shutdown();
		}
	}
}