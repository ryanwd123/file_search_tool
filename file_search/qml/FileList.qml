pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import fsearch

ListView {
    id: root1
    property int selected: 0
    property int filenameWidth: 12
    y: 80
    clip: true
    focus: false
    anchors.fill: parent
    interactive: true
    anchors.topMargin: 5
    anchors.leftMargin: 5
    anchors.bottomMargin: 5
    anchors.rightMargin: 5

    ScrollBar.vertical: ScrollBar {
        id: vbar
        policy: ScrollBar.AsNeeded
    }
    function scroll_zero() {
        vbar.position = 0;
    }

    function getVisibleRowCount() {
        var itemHeight = contentHeight / count;
        var visibleHeight = height;
        return Math.floor(visibleHeight / itemHeight);
    }

    function get_full_path() {
        if (model && model.rowCount() > 0 && selected >= 0 && selected < model.rowCount()) {
            // console.log(model.get_full_path(selected))
            return model.get_full_path(selected);
        }
        return "";
    }

    FontMetrics {
        id: fontMetrics
        // or whatever font you're using
        font.pixelSize: Utils.mainText + 5    // or your desired size
    }

    // property int fn_widht: parseInt(fontMetrics.advanceWidth('X') * 15)

    model: Backend.fileListModel
    delegate: Rectangle {
        id: box
        focus: false

        required property int index
        required property string filename
        required property string parent_folder
        required property string full_path
        required property string size
        required property string last_modified
        required property bool favorite
        required property bool is_folder

        height: root1.selected == index ? Utils.mainText + 7 : Utils.mainText + 5
        color: root1.selected == index ? 'lightblue' : mouse2.hovered ? '#f0f0f0' : 'white'
        width: parent ? parent.width : 0

        ContextMenu.menu: Menu {
            width: Utils.mainText * 20
            font.pixelSize: parent.height - 8

            MenuItemWithShortcut {
                mainText: "Open"
                shortcutText: "Enter"
                onTriggered: FileOps.openFile(box.full_path)
            }
            MenuItemWithShortcut {
                mainText: "Copy Path"
                shortcutText: "Ctrl+Shift+c"
                onTriggered: FileOps.copy(box.full_path)
            }
            MenuItemWithShortcut {
                mainText: "Reveal in Explorer"
                shortcutText: "Ctrl+e"
                onTriggered: FileOps.revealInExplorer(box.full_path)
            }
            MenuItemWithShortcut {
                mainText: FileOps.isOneDrive(box.full_path, "Copy Sharepoint Link")
                shortcutText: "Ctrl+t"
                onTriggered: /* ... */{}
            }
            MenuItemWithShortcut {
                mainText: FileOps.isOneDrive(box.full_path, "Open In Sharepoint")
                shortcutText: "Ctrl+Shift+t"
                onTriggered: /* ... */{}
            }
            MenuItemWithShortcut {
                mainText: FileOps.isOneDrive(box.full_path, "Open Sharepoint Folder")
                shortcutText: "Ctrl+g"
                onTriggered: /* ... */{}
            }
            MenuItemWithShortcut {
                mainText: box.favorite ? "Remove Favorite" : ""
                shortcutText: "Ctrl+r"
                onTriggered: {
                    AsyncRequest.deleteRecord('favorites', 'file_path', box.full_path);
                    box.favorite = false;
                }
            }
            MenuItemWithShortcut {
                mainText: box.favorite ? "" : "Add Favorite"
                shortcutText: "Ctrl+d"
                onTriggered: {
                    AsyncRequest.insertRecord('favorites', ['file_path'], [box.full_path]);
                    box.favorite = true;
                }
            }
            MenuItemWithShortcut {
                mainText: "Ignore Parent Folder"
                shortcutText: ""
                onTriggered: AsyncRequest.insertRecord('ignore_folders', ['file_path'], [box.parent_folder])
            }
        }

        Rectangle {
            id:row_rect
            color:box.color
            width:parent.width
            height:parent.height
            Row{
                
            Text {
                id: filename_label
                text: box.filename
                leftPadding:5
                clip:true
                font.weight: box.favorite ? Font.Bold : Font.Normal
                font.pixelSize: row_rect.height - 8
                width:Utils.mainText * root1.filenameWidth
                ToolTip.text:filename_label.text
                ToolTip.visible: implicitWidth > width && mouse2.hovered &&(
                    mouse2.point.position.x >= filename_label.x && 
                    mouse2.point.position.x <= filename_label.x + filename_label.width)
            }
            Text {
                id: parent_folder_label
                text: box.parent_folder
                clip:true
                font.pixelSize: filename_label.font.pixelSize
                width:row_rect.width - (
                    filename_label.width +
                    file_size_txt.width +
                    modified_txt.width
                )
                ToolTip.text:parent_folder_label.text
                ToolTip.visible: implicitWidth > width && mouse2.hovered &&(
                    mouse2.point.position.x >= parent_folder_label.x && 
                    mouse2.point.position.x <= parent_folder_label.x + parent_folder_label.width)
            
            }

            Text {
                id: file_size_txt
                text: box.size
                width:Utils.mainText*4
                font.pixelSize: filename_label.font.pixelSize
            }

            Text {
                id: modified_txt
                text: box.last_modified
                width:Utils.mainText*10
                font.pixelSize: filename_label.font.pixelSize
            }
        }}

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root1.selected = box.index;
            }
            onDoubleClicked: {
                root1.selected = box.index;
                FileOps.openFile(box.full_path);
            }
        }

        HoverHandler {
            id: mouse2
            acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
            cursorShape: Qt.PointingHandCursor

            // onHoveredChanged: {
            //     if (hovered) {
            //         root1.selected = box.index
            //     }
            // }
        }
    }
}
