from sklearn.tree import DecisionTreeClassifier

features = [[140,1], [130,1], [120,0], [110,0], [125,1]]
labels = ['Apple', 'Apple', 'Orange', 'Orange', 'Apple']

clf = DecisionTreeClassifier()

clf = clf.fit(features, labels)

inp_data = [[115, 0], [135, 1], [150, 1], [105, 0], [126, 1], [122, 0]]

prediction = clf.predict(inp_data)

print(prediction)