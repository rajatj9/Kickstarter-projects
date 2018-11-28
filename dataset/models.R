library(SuperLearner)
library(e1071)
library(leaps)
library(tree)
library(randomForest)
set.seed(3354)
setwd("/Users/pranavtalwar/Desktop/Kickstarter-projects/dataset")
data = read.csv("fixed_data1.csv")
nrow(data)
View(data)
data = data[,-1]

train = sample(nrow(data), nrow(data)*0.8)
data_train = data[train,]
data_test = data[-train,]
nrow(data_test)
nrow(data_train)


#logistic regression model - validation test
log.mod = glm(state~parent_category+funding_duration_days+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal,data = data_train,family = "binomial")
preds = predict(log.mod,data_test, type = "response")
options(scipen=999)
preds[preds>=0.5] = "successful"
preds[preds<0.5] = "failed"
table(preds, data_test$state)
summary(log.mod)

#random forest
kick.rf = randomForest(state~parent_category+funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal, data = data_train, mtry = 3, ntree = 500, importance = TRUE)
test_result.rf = predict(kick.rf, newdata = data_test)
test_result.rf
importance(kick.rf)
table(test_result.rf, data_test$state)
varImpPlot(kick.rf)

# bagging
kick.rf = randomForest(state~parent_category+funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal, data = data_train, mtry = 11, ntree = 500, importance = TRUE)
test_result.rf = predict(kick.rf, newdata = data_test)
test_result.rf
importance(kick.rf)
table(test_result.rf, data_test$state)
varImpPlot(kick.rf)

#trees
kick.tree = tree(state~parent_category+funding_duration_days+launch_month+country+staff_pick+creator_has_slug+blurb_length+blurb_word_count+name_length+name_word_count+usd_goal,data=data_train)
plot(kick.tree)
text(kick.tree, pretty = 0)
summary(kick.tree)
test_results.tree= predict(kick.tree, newdata= data_test)
success = test_results.tree[,2]
success[success>=0.5] = "successful"
success[success<0.5] = "failed"
table(success, data_test$state)

#cross validation and pruning of trees
cv.kick=cv.tree(kick.tree,FUN=prune.misclass)
names(cv.kick)
cv.kick
par(mfrow=c(1,2))
plot(cv.kick$size,cv.kick$dev,type="b")
plot(cv.kick$k,cv.kick$dev,type="b")
prune.kick=prune.misclass(kick.tree,best=3)
plot(prune.kick)
text(prune.kick,pretty=0)
tree.pred=predict(prune.kick,data_test,type="class")
tree.pred
table(tree.pred,data_test$state)



#best subset
regfit.full=regsubsets(usd_pledged~parent_categ, data = data_train,nvmax=13, really.big = T)
reg.summary = summary(regfit.full)
names(reg.summary)
plot(reg.summary$rss,xlab="Number of Variables",ylab="RSS",type="l")
plot(reg.summary$adjr2,xlab="Number of Variables",ylab="Adjusted RSq",type="l")
which.max(reg.summary$adjr2)
which.min(reg.summary$cp)
which.min(reg.summary$bic)
coefficients(regfit.full, id = 13)
plot(regfit.full, scale = "adjr2")

