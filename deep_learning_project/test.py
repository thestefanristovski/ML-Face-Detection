import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from load_data import *
from net import *

if __name__ == '__main__':
    net = Net()
    net = trainNet(train_loader)
    testNet(test_loader, net)
    # bootstrap the net
    net = bootstrapNet(net)
    testNet(test_loader, net)


def trainNet(train_loader, net):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    correct = 0
    total = 0
    # train
    for epoch in range(4):
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            images, labels = data
            # zero the parameter gradients
            optimizer.zero_grad()
            outputs = net(images)
            # print(outputs)
            # break
            # indice de la valeur max (0 pas face, 1, c'est face)
            _, predicted = torch.max(outputs.data, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0
    return net


def testNet(net, test_data):
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            outputs = net(images)
            # indice de la valeur max (0 pas face, 1, c'est face)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print('Accuracy of the network on the 10000 test images: %d %%' % (
        100 * correct / total))


def bootstrapNet(net):
    threshold = 0.8
    ceil = 0.2
    train_dir = './train_images_bootstrap'
    test_dir = './test_images_bootstrap'

    while threshold > 0.2:
        print(threshold)

        # get equal amount of data
        # train
        # test on the textures
        # keep the images that have over threshold in 1
        # inject those in train in non faces
        # repeat

        # get equal amount of data
        # load traindata
        train_data = torchvision.datasets.ImageFolder(
            train_dir, transform=transform)
        # get indices of train data and shuffle them
        indices_train = list(range(num_train))
        np.random.shuffle(indices_train)

        # create balancer sampler for train data
        train_sampler = ImbalancedDatasetSampler(
            train_data, indices=indices_train)

        # load train and test data
        train_data = torchvision.datasets.ImageFolder(
            train_dir, transform=transform)
        # these are our own textures
        test_data = torchvision.datasets.ImageFolder(
            test_dir, transform=transform)

        # get loaders
        train_loader = torch.utils.data.DataLoader(
            test_data, batch_size=batch_size, shuffle=True, num_workers=1)

        test_loader = torch.utils.data.DataLoader(
            test_data, batch_size=batch_size, shuffle=True, num_workers=1)

        # train the net
        net = trainNet(train_loader, net)

        # test for our textures and store the indices of images that
        # the net got wrong > threshold
        false_images_indices = []
        with torch.no_grad():
            for idx, data in enumerate(test_loader):
                images, labels = data
                outputs = net(images)
                # indice de la valeur max (0 pas face, 1, c'est face)

                proba = outputs.data[1]
                if proba >= threshold:
                    false_images_indices.append(idx)

        # inject too wrong textures into the train dataset

        threshold -= ceil
        ceil -= 0.05
