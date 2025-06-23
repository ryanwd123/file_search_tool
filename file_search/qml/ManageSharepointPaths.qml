pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
// import QtQuick.Dialogs
import QtQuick.Layouts
import QtCore

// import fsearch

Rectangle {
    id: root
    anchors.fill: parent
    color: '#90D2CD'
    property int textSize: 20
    MouseArea {
        anchors.fill: parent
    }

    Component.onCompleted: {
        populateFromSettings()
    }

    Settings {
        id: settings
        property string defaultSharepoint: ""
        property string sharepointFolders: ""
    }

    Text {
        id: closeInstructions
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 10
        anchors.rightMargin: 15
        text: "Esc to close"
        font.pixelSize: root.textSize - 4
        font.family: "consolas"
        color: 'darkred'
    }

    ListModel {
        id: model
    }

    function populateFromSettings() {
        model.clear();

        if (settings.defaultSharepoint !== "") {
            try {
                var defaultSharepoint = JSON.parse(settings.defaultSharepoint);
                if (Array.isArray(defaultSharepoint) && defaultSharepoint.length >= 2) {
                    mainSharepointLocalFolder.text = defaultSharepoint[0];
                    mainSharepointHttp.text = defaultSharepoint[1];
                }
            } catch (e) {
                console.log("Error parsing defaultSharepoint settings:", e);
            }
        }

        if (settings.sharepointFolders !== "") {
            try {
                var sharepointFolders = JSON.parse(settings.sharepointFolders);
                if (Array.isArray(sharepointFolders)) {
                    for (var i = 0; i < sharepointFolders.length; i++) {
                        var folder = sharepointFolders[i];
                        if (Array.isArray(folder) && folder.length >= 2) {
                            model.append({
                                local: folder[0],
                                url: folder[1]
                            });
                        }
                    }
                }
            } catch (e) {
                console.log("Error parsing sharepointFolders settings:", e);
            }
        }
    }

    ColumnLayout {
        // anchors.top: parent.top
        anchors.fill: parent
        // anchors.left: parent.left
        // anchors.right: parent.right
        anchors.margins: 10
        spacing: 10

        Text {
            Layout.alignment: Qt.AlignCenter
            Layout.maximumHeight: implicitHeight
            text: 'Sharepoint Config'
            font.pixelSize: root.textSize + 20
            font.family: "consolas"
        }

        Text {
            Layout.alignment: Qt.AlignLeft
            font.family: "consolas"
            font.pixelSize: root.textSize
            text: 'default sharepoint mappping:'
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true
            Layout.maximumHeight: implicitHeight
            // Layout.alignment: Qt.AlignCenter
            Layout.alignment: Qt.AlignTop
            TextField {
                id: mainSharepointLocalFolder
                Layout.fillWidth: true
                placeholderText: 'Local Folder e.g. C:\\users\\user\\org\\'
                font.pixelSize: root.textSize
            }
            TextField {
                id: mainSharepointHttp
                Layout.fillWidth: true
                placeholderText: 'Root Url e.g http://something.org.../site/'
                font.pixelSize: root.textSize
            }
        }

        Text {
            Layout.alignment: Qt.AlignLeft
            font.family: "consolas"
            font.pixelSize: root.textSize
            text: 'Additional Folders:'
        }
        Button {
            Layout.alignment: Qt.AlignLeft
            font.family: "consolas"
            font.pixelSize: root.textSize
            text: 'Add Item'
            onClicked: {
                model.append({
                    local: "",
                    url: ""
                });
                console.log(model.count);
            }
        }

        ListView {
            id: listv
            Layout.fillWidth: true
            Layout.fillHeight: true

            model: model
            delegate: RowLayout {
                id: input

                height: implicitHeight + 5
                required property int index
                required property string local
                required property string url
                onLocalChanged: console.log(local)

                width: parent.width
                // RowLayout{
                TextField {
                    id: inputLocal
                    Layout.fillWidth: true
                    placeholderText: 'Local Folder'
                    font.pixelSize: root.textSize
                    text: input.local
                    onEditingFinished: {
                        if (text !== input.local) {
                            model.setProperty(input.index, "local", text);
                        }
                    }
                }
                TextField {
                    id: inputUrl
                    Layout.fillWidth: true
                    placeholderText: 'Root Url'
                    font.pixelSize: root.textSize
                    text: input.url
                    onEditingFinished: {
                        if (text !== input.url) {
                            model.setProperty(input.index, "url", text);
                        }
                    }
                }
                Button {
                    text: "delete"
                    onClicked: model.remove(input.index)
                    font.pixelSize: root.textSize
                    font.family: "consolas"
                }
            }
        }
        Button {
            Layout.alignment: Qt.AlignRight
            font.family: "consolas"
            font.pixelSize: root.textSize
            text: 'Save'
            onClicked: {
                if (mainSharepointLocalFolder.text != "" && mainSharepointHttp.text != "") {
                    var defaultSharepoint = [mainSharepointLocalFolder.text, mainSharepointHttp.text];
                    settings.defaultSharepoint = JSON.stringify(defaultSharepoint);
                }
                var sharepointFolders = [];
                for (var i = 0; i < model.count; i++) {
                    var item = model.get(i);
                    if (item.local != "" && item.url != "") {
                        sharepointFolders.push([item.local, item.url]);
                    }
                }
                settings.sharepointFolders = JSON.stringify(sharepointFolders);
            }
        }
    }
}
