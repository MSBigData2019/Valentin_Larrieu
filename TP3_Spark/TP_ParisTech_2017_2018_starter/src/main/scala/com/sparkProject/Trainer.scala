package com.sparkProject

import org.apache.spark.SparkConf
import org.apache.spark.sql.SparkSession
import org.apache.spark.SparkConf
import org.apache.spark.ml.feature.RegexTokenizer
import org.apache.spark.sql.SparkSession
import org.apache.spark.ml.feature.{CountVectorizer, IDF, StopWordsRemover, StringIndexer, OneHotEncoder,VectorAssembler}
import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.tuning.{ParamGridBuilder, TrainValidationSplit}
import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator




object Trainer {

  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAll(Map(
      "spark.scheduler.mode" -> "FIFO",
      "spark.speculation" -> "false",
      "spark.reducer.maxSizeInFlight" -> "48m",
      "spark.serializer" -> "org.apache.spark.serializer.KryoSerializer",
      "spark.kryoserializer.buffer.max" -> "1g",
      "spark.shuffle.file.buffer" -> "32k",
      "spark.default.parallelism" -> "12",
      "spark.sql.shuffle.partitions" -> "12",
      "spark.driver.maxResultSize" -> "2g"
    ))

    val spark = SparkSession
      .builder
      .config(conf)
      .appName("TP_spark")
      .getOrCreate()


    /*******************************************************************************
      *
      *       TP 3
      *
      *       - lire le fichier sauvegarder précédemment
      *       - construire les Stages du pipeline, puis les assembler
      *       - trouver les meilleurs hyperparamètres pour l'entraînement du pipeline avec une grid-search
      *       - Sauvegarder le pipeline entraîné
      *
      *       if problems with unimported modules => sbt plugins update
      *
      ********************************************************************************/

    println("hello world ! from Trainer")

    // Question 1
    val data = spark.read.parquet("/root/Documents/Project/TP_ParisTech_2018_2019_starter/TP_ParisTech_2017_2018_starter/src/main/resources/prepared_trainingset")

    // 2.a
    println(" 2 a/ Tokenizer")
    val tokenizer = new RegexTokenizer()
      .setPattern("\\W+")
      .setGaps(true)
      .setInputCol("keywords")
      .setOutputCol("tokens")

    // 2.b
    println(" 2 b/ StopWordsRemover")
    val remover = new StopWordsRemover()
      .setInputCol(tokenizer.getOutputCol)
      .setOutputCol("removed")

    // 2.c
    println(" 2 c/ CountVectorizer")
    val vectorizer = new CountVectorizer()
      .setInputCol(remover.getOutputCol)
      .setOutputCol("vectorized")

    // 2.d
    println(" 2 d/ Idf")
    val idf = new IDF()
      .setInputCol(vectorizer.getOutputCol)
      .setOutputCol("tfidf")

    // Question 3

    // 3.e
    println(" 3 e/ String Indexer country")
    val countryConv = new StringIndexer()
      .setInputCol("country2")
      .setOutputCol("country_indexed")
      .setHandleInvalid("skip")

    // 3.f
    println(" 3 f/ String Indexer currency")
    val currencyConv = new StringIndexer()
      .setInputCol("currency2")
      .setOutputCol("currency_indexed")
    //.setHandleInvalid("skip")
    //keep

    // 3.g
    println(" 3 g/ One hot encoder country")
    val countryHot = new OneHotEncoder()
      .setInputCol(countryConv.getOutputCol)
      .setOutputCol("country_onehot")

    val currencyHot = new OneHotEncoder()
      .setInputCol(currencyConv.getOutputCol)
      .setOutputCol("currency_onehot")

    // Question 4

    // 4.h
    println(" 4 h/ VectorAssembler")
    val vectorAssembler = new VectorAssembler()
      .setInputCols(Array("tfidf", "days_campaign", "hours_prepa", "goal", "country_onehot", "currency_onehot"))
      .setOutputCol("features")

    // 4.i
    println(" 4 i/ Logistic regression")
    val lr = new LogisticRegression()
      .setElasticNetParam(0.0)
      .setFitIntercept(true)
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setStandardization(true)
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setThresholds(Array(0.7, 0.3))
      .setTol(1.0e-6)
      .setMaxIter(300)

    // 4.j
    println(" 4 j/ Pipeline")
    val stages = Array(tokenizer, remover, vectorizer, idf, countryConv, currencyConv, countryHot, currencyHot, vectorAssembler, lr)
    val pipeline = new Pipeline().setStages(stages)

    // Question 5
    println(" 5/ Split")
    val SEED = 12345
    // 5.k
    val Array(trainData, testData) = data.randomSplit(Array(0.9, 0.1), seed = SEED)

    // 5.l
    println(" 5 l/ TrainValidationSplit")

    val evaluator =  new MulticlassClassificationEvaluator()
      .setLabelCol("final_status")
      .setPredictionCol("predictions")
      .setMetricName("f1")


    val paramGrid = new ParamGridBuilder()
      .addGrid(vectorizer.minDF, Array(55.0, 75.0, 95.0))
      .addGrid(lr.regParam, Array(10e-8, 10e-6, 10e-4, 10e-2))
      .build()


    val trainValidationSplit = new TrainValidationSplit()
      .setEstimator(pipeline)
      .setEvaluator(evaluator)
      .setEstimatorParamMaps(paramGrid)
      .setTrainRatio(0.7)

    // 5.m
    println(" 5 m/ Fit and transform")
    val model = trainValidationSplit.fit(trainData)

    val df_WithPredictions = model.transform(testData)

    // 5.n
    println(" 5 n/ Count results & score")
    df_WithPredictions.groupBy("final_status", "predictions").count.show()

    val myMetrics = evaluator.evaluate(df_WithPredictions.select("features", "final_status", "predictions", "raw_predictions"))

    println("f1score : "+ myMetrics)

    /*Results optained with this seed :
    +------------+-----------+-----+
    |final_status|predictions|count|
    +------------+-----------+-----+
    |           1|        0.0|  979|
    |           0|        0.0| 3822|
    |           1|        1.0| 2399|
    |           0|        1.0| 3447|
    +------------+-----------+-----+
    f1score : 0.5974092144793134
     */









  }
}
