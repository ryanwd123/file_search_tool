pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import fsearch

Rectangle {
    id: root
    property string table: "folders_to_index"
    property string column: "file_path"

    anchors.fill: parent
    color: '#90D2CD'

    MouseArea {
        anchors.fill: parent
    }

    Component.onCompleted: {
        root.updateList();
        // root.focus = true;
        listv.focus = true;
        listv.forceActiveFocus();
    }

    function removeSelected() {
        if (listv.currentIndex < 0) {
            return;
        }
        var txt = model.get(listv.currentIndex).path;
        AsyncRequest.deleteRecord(table, column, txt);
        updateList();
        listv.forceActiveFocus();
    }

    function updateList() {
        AsyncRequest.request({
            command: "sql_command",
            sql: `SELECT ${column} from ${table}`
        }).then(function (results) {
            var data = results.result.map(x => x[0]);
            model.clear();
            for (var i = 0; i < data.length; i++) {
                model.append({
                    "path": data[i]
                });
            }
            listv.forceActiveFocus();
        }).catch(function (error) {
            console.log("error adding rec file: " + error);
        });
    }

    Text {
        id: closeInstructions
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 10
        anchors.rightMargin: 15
        text: "Esc to close"
        font.pixelSize: Utils.mainText - 4
        font.family: "consolas"
        color: 'darkred'
    }

    ListModel {
        id: model
    }

    FolderDialog {
        id: folderDialog
        title: "Select Folder to Add"
        onAccepted: {
            var path = selectedFolder.toString();
            path = FileOps.uri_to_path(path)
            AsyncRequest.insertRecord(root.table, [root.column], [path]);
            console.log(path);
            root.updateList();
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        Text {
            Layout.alignment: Qt.AlignCenter
            text: 'Manage Table: ' + root.table
            font.pixelSize: Utils.mainText + 20
            font.family: "consolas"
        }
        Row {
            spacing: 20
            Layout.alignment: Qt.AlignCenter
            Button {
                text: "Add Item"
                font.pixelSize: Utils.mainText - 2
                font.family: "consolas"
                onClicked: folderDialog.open()
                Keys.onReturnPressed:folderDialog.open()
                
                // Keys.onPressed: function (event) {
                //     if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                //         folderDialog.open();
                //         event.accepted = true;
                //     }
                // }
            }

            Button {
                text: "Remove Item"
                font.pixelSize: Utils.mainText - 2
                font.family: "consolas"
                onClicked: root.removeSelected()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: 'white'
            // border.color: listv.focus ? 'red' : 'black'
            border.color: 'black'
            border.width: 2
            radius: 5

            ListView {
                id: listv
                focus: true
                focusPolicy: Qt.StrongFocus
                anchors.fill: parent
                anchors.margins: 10
                clip: true
                spacing: 2
                model: model
                delegate: ManageTableListDelegate {
                    lv: listv
                    width: listv.width
                }
            }
        }
    }
}
