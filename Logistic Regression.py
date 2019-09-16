from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def logReg(uDiffs, choices):
    logmodel = LogisticRegression()
    logmodel.fit(X_train, y_train)

    return



X_train, X_test, y_train, y_test = \
    train_test_split(train.drop('Survived',axis=1),
           train['Survived'], test_size=0.30,
            random_state=101)

Predictions = logmodel.predict(X_test)  # Test if the estimated values are predictive

print(classification_report(y_test, Predictions))