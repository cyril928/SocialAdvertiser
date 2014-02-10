package edu.ntu.pp2011;

import java.util.*;
import java.lang.StringBuilder;
import java.io.*;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.util.*;

import org.apache.hadoop.filecache.DistributedCache;
import org.apache.hadoop.mapred.lib.db.*;
import java.net.URI;
import java.sql.*;

// our base class
public class UserIndex 
{
	static class UserRecord implements Writable, DBWritable
	{
		public double[] score;
		public String uuid;

		public UserRecord(String uuid, double[] score){
			this.score = score;
			this.uuid = uuid;
		}

		public void readFields(DataInput in) throws IOException{
			this.uuid= Text.readString(in);
			for(int i=0; i<25; i++)
				this.score[i] = in.readDouble();
		}

		public void write(DataOutput out) throws IOException{
			Text.writeString(out,this.uuid);
			for(int i=0; i<25; i++)
				out.writeDouble(score[i]);
		}

		public void readFields(ResultSet result)throws SQLException     {
			for (int i=2; i<27; i++)
				this.score[i-2] = result.getDouble(i);
			this.uuid= result.getString(1);
		}

		public void write(PreparedStatement stmt) throws SQLException{
			stmt.setString(1, this.uuid);
			for(int i=2;i<27;i++)
				stmt.setDouble(i,this.score[i-2]);
		}

		public String toString(){
			StringBuilder str = new StringBuilder(this.uuid);

			for(int i =0;i<25;i++)
			{    str.append(" ");
				str.append(score[i]);
			}
			return str.toString();
		}
	}

	// parse input file into items
	public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text>
	{
		public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException
		{
			String[] line;
			String uuid, interest;
			StringBuilder sb = new StringBuilder();
			Scanner sc = new Scanner(value.toString());
			int raw_score;

			while ( sc.hasNextLine() )
			{
				line = sc.nextLine().split(",");

				// if it's a friend's choice we give it 1 pt, otherwise 2 pts.
				if( line[0].indexOf(':')==-1 )
				{
					raw_score = 2;
					uuid = line[0];
					interest = line[1];
				}
				else
				{
					raw_score = 1;
					uuid = line[0].split(":")[0];
					interest = line[1];
				}

				sb.append(uuid);
				sb.append(':');
				sb.append(interest);

				// output: ("uuid:raw_catagory", "raw_score")
				output.collect(new Text(sb.toString()), new Text(Integer.toString(raw_score)));
			}
		}
	}

	// local aggregation
	public static class Combine extends MapReduceBase implements Reducer<Text, Text, Text, Text>
	{
		public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException
		{
			String[] line = key.toString().split(":");
			String uuid = line[0];
			String interest = line[1];
			StringBuilder sb = new StringBuilder();
			int local_sum = 0;
			while( values.hasNext() )
				local_sum += Integer.parseInt(values.next().toString());

			sb.append(interest);
			sb.append(':');
			sb.append(local_sum);

			// output: ("uuid", "raw_category:raw_score_local_sum")
			output.collect(new Text(uuid), new Text(sb.toString()));
		}
	}

	// sum up the count vector
	public static class Reduce extends MapReduceBase implements Reducer<Text, Text, Text, Text>
	{
		private Path[] localFiles;
		private String[] category;

		// retrieve conversion table
		public void configure(JobConf job)
		{
			try
			{
				localFiles = DistributedCache.getLocalCacheFiles(job);
				category = new String[143];
				BufferedReader br = new BufferedReader(new FileReader(localFiles[0].toString()));
				String line;
				int i = 0;
				while((line = br.readLine())!= null)
				{
					String[] tmp= line.split(":");
					category[i] = tmp[0];
					i++;
				}
				br.close();
			}
			catch (IOException e)
			{
				System.out.println(e);
			}
		}

		public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException 
		{
			String[] value;
			String interest;
			int count;
			double[] vector = new double[143];
			double sum = 0.0;
			StringBuilder sb = new StringBuilder();
			int index = -1;

			while( values.hasNext() )
			{
				value = values.next().toString().split(":");
				interest = value[0];
				count = Integer.parseInt(value[1]);
				if( (index=Arrays.binarySearch(category, interest))>=0 )
				{
					vector[index] += count;
					sum += count;
				}
				else
				{
					System.err.println(interest);
				}
			}

			for( int i=0; i<143; i++ )
			{
				sb.append(vector[i]/sum);
				sb.append(',');
			}
			sb.deleteCharAt(sb.length()-1);

			// output: ("uuid", "tfidf_vector_csv")
			output.collect(key, new Text(sb.toString()));
		}
	}

	// tfidf to membership degree conversion
	public static class Map2 extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text>
	{
		private Path[] localFiles;
		private double[][] scoreMatrix;

		public void configure(JobConf job)
		{
			try{
				localFiles = DistributedCache.getLocalCacheFiles(job);
				scoreMatrix =  new double[143][25];
				BufferedReader br =new BufferedReader(new FileReader(localFiles[0].toString()));
				String line;
				int i = 0;
				while((line = br.readLine())!= null){
					String[] tmp= line.split(",");
					for(int j=0;j<25;j++)
						scoreMatrix[i][j]= Double.parseDouble(tmp[j+1]);
					i++;
				}
				br.close();
			}catch (IOException e){System.out.println(e);}
		}

		public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException
		{
			String[] input = value.toString().split("\t");
			String[] vectortmp= input[1].split(",");
			double[] vectorin = new double[143];
			double[] vectorout= new double[25];
			StringBuilder tmp = new StringBuilder();
			//parse input string vector to double array
			for(int i=0;i<143;i++)
				vectorin[i] = Double.parseDouble(vectortmp[i]);
			for(int i=0;i<25;i++)
				vectorout[0]=0;

			//do matrix multiplication
			for(int i=0;i<25;i++)
			{
				for(int j=0;j<143;j++)
				{
					vectorout[i] += vectorin[j] * scoreMatrix[j][i];
				}
				tmp.append(vectorout[i]);
				if(i !=24)
					tmp.append(",");
			}
			output.collect(new Text(input[0]),new Text(tmp.toString()));

		}
	}

	// final output to database
	public static class Reduce2 extends MapReduceBase implements Reducer<Text, Text, UserRecord, NullWritable>
	{
		public void reduce(Text key, Iterator<Text> values, OutputCollector<UserRecord, NullWritable> output, Reporter reporter) throws IOException
		{
			while(values.hasNext())
			{
				String[] value = values.next().toString().trim().split(",");
				double[] score= new double[25];
				for(int i=0;i<25;i++){
					score[i] = Double.parseDouble(value[i]);
				}
				UserRecord record = new UserRecord(key.toString(),score);
				output.collect(record,NullWritable.get());
			}


		}
	}

	public static void main(String[] args) throws Exception 
	{
		// step 1: from input to tfidf feature vector
		JobConf conf = new JobConf(UserIndex.class);
		conf.setJobName("UserIndex_accouting");
		DistributedCache.addCacheFile(new URI("/user/shared/SimilarityScoreboard.csv"), conf);

		// mapper
		conf.setMapperClass(Map.class);
		conf.setMapOutputKeyClass(Text.class);
		conf.setMapOutputValueClass(Text.class);

		// combiner
		conf.setCombinerClass(Combine.class);

		// reducer
		conf.setReducerClass(Reduce.class);
		conf.setOutputKeyClass(Text.class);
		conf.setOutputValueClass(Text.class);

		// I/O format
		conf.setInputFormat(TextInputFormat.class);
		conf.setOutputFormat(TextOutputFormat.class);

		// I/O path
		FileInputFormat.setInputPaths(conf, new Path(args[0]));
		FileOutputFormat.setOutputPath(conf, new Path(args[1]));

		// run job
		JobClient.runJob(conf);

		// step 2: from tfidf vector to final characteristic vector
		JobConf conf2 = new JobConf(UserIndex.class);
		conf2.setJobName("UserIndex_projection");
        	DistributedCache.addCacheFile(new URI("/user/shliew/SimilarityScoreboard.csv"), conf2);
		DistributedCache.addFileToClassPath(new Path("/user/shared/mysql-connector-java-5.1.16-bin.jar"), conf2);
		DBConfiguration.configureDB(conf2, "com.mysql.jdbc.Driver","jdbc:mysql://140.112.29.234/socialadvertiser","socialadvertiser","socialaddb");
		String[] fields = {"`uuid`","`Arts & Crafts & Sewing`","`Automotive`","`Baby`","`Beauty`","`Books`","`Cell phones & accessories`",
			"`Clothing & accessories`","`Electronic`","`Grocery & Gourmet Food`","`Health & personal care`",
			"`Home & Garden & pets`","`Industrial & Scientific`","`Jewelry`","`Magazine subsriptions`",
			"`Movies & TV`","`Music`","`Musical Instruments`","`Office products`","`Shoes`","`Software`",
			"`Sports & Outdoors`","`Tools & Home Improvement`","`Toys & Games`","`Video Games`","`Watches`"};

		// mapper
		conf2.setMapperClass(Map2.class);
		conf2.setMapOutputKeyClass(Text.class);
		conf2.setMapOutputValueClass(Text.class);

		// reducer
		conf2.setReducerClass(Reduce2.class);
		conf2.setOutputKeyClass(Text.class);
		conf2.setOutputValueClass(UserRecord.class);

		// I/O format
		conf2.setInputFormat(TextInputFormat.class);
		conf2.setOutputFormat(DBOutputFormat.class);

		// I/O path
		FileInputFormat.setInputPaths(conf2, new Path(args[1]));
		DBOutputFormat.setOutput(conf2, "userrank", fields);

		// run job
		JobClient.runJob(conf2);
	}
}


