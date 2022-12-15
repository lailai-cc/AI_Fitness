import csv
import pandas as pd
from tensorflow import keras
from sklearn.model_selection import train_test_split
from data import BodyPart 
import tensorflow as tf
import tensorflowjs as tfjs

from matplotlib import pyplot as plt

tfjs_model_dir = 'model'


# 加载预处理后的训练集和测试集CSV文件
def load_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.drop(['filename'], axis=1, inplace=True)

    # 提取类名列表
    classes = df.pop('class_name').unique()

    # 提取标签
    y = df.pop('class_no')

    # 将输入特征和标签转换为便于模型训练的格式
    X = df.astype('float64')
    y = keras.utils.to_categorical(y)
    
    return X, y, classes

# 得到两个关键点的中心点
def get_center_point(landmarks, left_bodypart, right_bodypart):
    left = tf.gather(landmarks, left_bodypart.value, axis=1)
    right = tf.gather(landmarks, right_bodypart.value, axis=1)
    center = left * 0.5 + right * 0.5
    return center

# 计算整体姿态的大小
def get_pose_size(landmarks, torso_size_multiplier=2.5):
    # 臀部中心
    hips_center = get_center_point(landmarks, BodyPart.LEFT_HIP, BodyPart.RIGHT_HIP)
    # 肩部中心
    shoulders_center = get_center_point(landmarks, BodyPart.LEFT_SHOULDER, BodyPart.RIGHT_SHOULDER)

    # 躯干尺寸作为最小身体尺寸
    torso_size = tf.linalg.norm(shoulders_center - hips_center)

    # 姿态中心
    pose_center_new = get_center_point(landmarks, BodyPart.LEFT_HIP, BodyPart.RIGHT_HIP)
    pose_center_new = tf.expand_dims(pose_center_new, axis=1)
    pose_center_new = tf.broadcast_to(pose_center_new, [tf.size(landmarks) // (17*2), 17, 2])

    d = tf.gather(landmarks - pose_center_new, 0, axis=0, name="dist_to_pose_center")
    max_dist = tf.reduce_max(tf.linalg.norm(d, axis=0))

    # 标准化
    pose_size = tf.maximum(torso_size * torso_size_multiplier, max_dist)
    return pose_size


# 将姿态中心移动到(0,0)并将其缩放到恒定的位姿大小
def normalize_pose_landmarks(landmarks):
    pose_center = get_center_point(landmarks, BodyPart.LEFT_HIP, BodyPart.RIGHT_HIP)
    pose_center = tf.expand_dims(pose_center, axis=1)
    pose_center = tf.broadcast_to(pose_center, [tf.size(landmarks) // (17*2), 17, 2])
    landmarks = landmarks - pose_center
    pose_size = get_pose_size(landmarks)
    landmarks /= pose_size
    return landmarks

# 转换为特征向量
def landmarks_to_embedding(landmarks_and_scores):
    reshaped_inputs = keras.layers.Reshape((17, 3))(landmarks_and_scores)
    landmarks = normalize_pose_landmarks(reshaped_inputs[:, :, :2])
    embedding = keras.layers.Flatten()(landmarks)
    return embedding

# 预处理
def preprocess_data(X_train):
    processed_X_train = []
    for i in range(X_train.shape[0]):
        embedding = landmarks_to_embedding(tf.reshape(tf.convert_to_tensor(X_train.iloc[i]), (1, 51)))
        processed_X_train.append(tf.reshape(embedding, (34)))
    return tf.convert_to_tensor(processed_X_train)


X, y, class_names = load_csv('train_data.csv')

# 将其拆分为训练集(85%)和验证集(15%)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15)
X_test, y_test, _ = load_csv('test_data.csv')

processed_X_train = preprocess_data(X_train)
# print(processed_X_train)
processed_X_val = preprocess_data(X_val)
processed_X_test = preprocess_data(X_test)

# 构建神经网络模型
inputs = tf.keras.Input(shape=(34))
layer = keras.layers.Dense(128, activation=tf.nn.relu6)(inputs)
layer = keras.layers.Dropout(0.5)(layer)
layer = keras.layers.Dense(64, activation=tf.nn.relu6)(layer)
layer = keras.layers.Dropout(0.5)(layer)
outputs = keras.layers.Dense(len(class_names), activation="softmax")(layer)

model = keras.Model(inputs, outputs)

# 编译
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

checkpoint_path = "weights.best.hdf5"
checkpoint = keras.callbacks.ModelCheckpoint(checkpoint_path,
                             monitor='val_accuracy',
                             verbose=1,
                             save_best_only=True,   # only keep the best model
                             mode='max')
earlystopping = keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=20)

print('--------------TRAINING----------------')
history = model.fit(processed_X_train, y_train,
                    epochs=200,
                    batch_size=16,
                    validation_data=(processed_X_val, y_val),
                    callbacks=[checkpoint, earlystopping])

print('-----------------EVAUATION----------------')
loss, accuracy = model.evaluate(processed_X_test, y_test)
print('LOSS: ', loss)
print("ACCURACY: ", accuracy)

# 保存模型
tfjs.converters.save_keras_model(model, tfjs_model_dir)
print('tfjs model saved at ',tfjs_model_dir)

# 将训练过程可视化
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['TRAIN', 'VAL'], loc='lower right')
plt.show()