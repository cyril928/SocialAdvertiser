PROJ=UserIndex
JarFile=$(PROJ).jar
MainFunc=edu.ntu.pp2011.$(PROJ)
LocalOutDir="/tmp/$$USER/$(PROJ)_output"
dfsinput=/user/shared/sa
dfsoutput=$(PROJ)-output
backupdata= /user/shared/processed_data
LocalInDir= /home/cyril928/mysite/usermap

all: class jar run

class:
	#-rm -rf $(PROJ)
	-mkdir -p $(PROJ)
	-rm -f ./$(PROJ)/*.class
	-rm -rf ./$(PROJ)/edu
	javac -classpath ./$(PROJ):$$CLASSPATH:/usr/local/hadoop/hadoop-0.20.2-core.jar -d $(PROJ) $(PROJ).java

jar:
	-rm -f $(JarFile)
	jar cvf $(JarFile) -C $(PROJ) .

run:
	-hadoop fs -rmr $(dfsoutput)
	hadoop jar $(JarFile) $(MainFunc) $(dfsinput) $(dfsoutput)
	hadoop fs -mv $(dfsinput)/* $(backupdata)

output:
	rm -rf $(LocalOutDir)
	hadoop fs -get $(dfsoutput) $(LocalOutDir)
	cp $(LocalOutDir)/part-00000 ./out
	-hadoop fs -rmr $(dfsoutput)

clean:
	-rm -f ./out
	-rm -f *.jar
	-rm -f ./$(PROJ)/*.class
	-rm -rf ./$(PROJ)/edu

help:
	@echo "Usage:"
	@echo " make class   - Compile to class file."
	@echo " make jar     - Build Jar File."
	@echo " make clean   - Clean up Output directory on HDFS."
	@echo " make run     - Run your MapReduce code on Hadoop."
	@echo " make output  - Download output file."
	@echo " make help    - Show Makefile options."
	@echo " "
	@echo "Example:"
	@echo " make class && make jar && make run && make output && make clean"
