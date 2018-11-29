library(SuperLearner)
library(e1071)
library(leaps)
library(tree)
library(randomForest)
set.seed(3354)
setwd("/Users/pranavtalwar/Desktop/Kickstarter-projects/dataset")
data= read.csv("fixed_data1.csv")
nrow(data)
str(data)
data = data[,-1]
data[, 6] = sapply(data[, 6], as.character)
for (i in 1:nrow(data)){
  if(data$country[i]!="US")
  {
    data$country[i] = "Other"
  }
}
data[, 6] = sapply(data[, 6], as.factor)
data$launch_month = as.factor(data$launch_month)
data$deadline_month = as.factor(data$deadline_month)
str(data)
summary(data)

View(data)

train = sample(nrow(data), nrow(data)*0.7)
data_train = data[train,]
data_test = data[-train,]
nrow(data_test)
nrow(data_train)
summary(data)


#logistic regression model - validation test
names(data)
log.mod = glm(state~parent_category+funding_duration_days+pre_funding_duration_days+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_word_count+usd_goal,data = data_train,family = "binomial")
preds = predict(log.mod,data_test, type = "response")
preds2 = predict(log.mod, data_train, type = "response")
options(scipen=999)
preds[preds>=0.5] = "successful"
preds[preds<0.5] = "failed"
preds2[preds2>=0.5] = "successful"
preds2[preds2<0.5] = "failed"
table(preds, data_test$state)
table(preds2, data_train$state)
summary(log.mod)

#random forest
kick.rf = randomForest(state~parent_category+funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal, data = data_train, mtry = 3, ntree = 500, importance = TRUE)
test_result.rf = predict(kick.rf, newdata = data_test)
train_result.rf = predict(kick.rf, newdata = data_train)
test_result.rf
importance(kick.rf)[,1]
table(test_result.rf, data_test$state)
table(train_result.rf, data_train$state)

varImpPlot(kick.rf, main = "Important Variables")

# bagging
kick.rf = randomForest(state~parent_category+funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal, data = data_train, mtry = 11, ntree = 500, importance = TRUE)
test_result.rf = predict(kick.rf, newdata = data_test)
train_result.rf = predict(kick.rf, newdata = data_train)
table(test_result.rf, data_test$state)
table(train_result.rf, data_train$state)
importance(kick.rf)
varImpPlot(kick.rf, main = "Important Variables (Bagging)")

#trees
kick.tree = tree(state~parent_category+funding_duration_days+pre_funding_duration_days+launch_month+country+location.type+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal,data=data_train)
plot(kick.tree)
text(kick.tree, pretty = 0)
summary(kick.tree)
test_results.tree= predict(kick.tree, newdata= data_test)
success = test_results.tree[,2]
success[success>=0.5] = "successful"
success[success<0.5] = "failed"
table(success, data_test$state)

train_results = predict(kick.tree, newdata = data_train)
success_train = train_results[,2]
success_train[success_train>=0.5] = "successful"
success_train[success_train<0.5] = "failed"
table(success_train, data_train$state)

#cross validation and pruning of trees
cv.kick=cv.tree(kick.tree,FUN=prune.misclass)
names(cv.kick)
cv.kick
par(mfrow=c(1,2))
plot(cv.kick$size,cv.kick$dev,type="b")
plot(cv.kick$k,cv.kick$dev,type="b")
prune.kick=prune.misclass(kick.tree,best=4)
plot(prune.kick)
text(prune.kick,pretty=0)
tree.pred=predict(prune.kick,data_test,type="class")
tree.pred
table(tree.pred,data_test$state)

#nb
NB = naiveBayes(state~parent_category+pre_funding_duration_days+funding_duration_days+location.type+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal,data= data_train)
summary(NB)
NB_pred=predict(NB,data_test)
NB_preds = predict(NB, data_train)
library(gmodels)
CrossTable(data_test$state, NB_pred, 
           prop.chisq = FALSE, prop.c = FALSE, 
           prop.r = FALSE, dnn = c('actual state', 'predicted state')) 
CrossTable(data_train$state, NB_preds, 
           prop.chisq = FALSE, prop.c = FALSE, 
           prop.r = FALSE, dnn = c('actual state', 'predicted state')) 
#adding laplace estimator
NB = naiveBayes(state~parent_category+pre_funding_duration_days+launch_month+country+staff_pick+location.type+creator_has_slug+blurb_length+blurb_word_count+name_word_count+usd_goal+name_length,data= data_train, laplace = 1)
NB_pred = predict(NB, data_test)
CrossTable(data_test$state, NB_pred, 
           prop.chisq = FALSE, prop.c = FALSE, 
           prop.r = FALSE, dnn = c('actual state', 'predicted state')) 

#neuralnet
library(neuralnet)
library(nnet)
scl <- function(x){ (x - min(x))/(max(x) - min(x)) }
data$parent_category = as.numeric(factor(data$parent_category))




data$location.type = as.numeric(factor(data$location.type))
data$creator_has_slug = as.numeric(factor(data$creator_has_slug))
data$funding_duration_days = scl(data$funding_duration_days)
data$pre_funding_duration_days = scl(data$funding_duration_days)
data$blurb_length = scl(data$blurb_length)
data$blurb_word_count = scl(data$blurb_word_count)
data$name_length = scl(data$name_length)
data$name_word_count = scl(data$name_word_count)
data$usd_goal = scl(data$usd_goal)
data$usd_pledged = scl(data$usd_pledged)
data$backers_count = scl(data$backers_count)
nn = neuralnet(state~parent_category+pre_funding_duration_days+launch_month+country+staff_pick+location.type+creator_has_slug+blurb_length+blurb_word_count+name_word_count+usd_goal+name_length,
                data = data_train)


#svm
svm.mod = svm(state~parent_category+pre_funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_word_count+usd_goal+name_length, data=data_train, cost = 10)
summary(svm.mod)
pred = predict(svm.mod, data_test, decision.values = TRUE)
table(preds, data_test$state)
pred

#mulptiple linear regression
multilinear = lm(usd_pledged~funding_duration_days+pre_funding_duration_days+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count, data=data_train)
summary(multilinear)
preds = predict(multilinear, data_test)
mean((preds-log(data_test$usd_pledged))^2)







