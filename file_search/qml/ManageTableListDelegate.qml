import QtQuick

Rectangle {
    id: delegateRect

    required property ListView lv
    required property int index
    required property string path
    readonly property bool isSelected: lv.currentIndex === index
    readonly property bool isHovered: mouse3.containsMouse
    color: isSelected ? '#FEECA2' : isHovered ? 'lightgray' : 'white'
    border.color: isSelected ? '#ccc' : 'white'
    radius: 3
    implicitHeight: label.implicitHeight
    Text {
        id: label
        padding: 2
        leftPadding: 5
        text: delegateRect.path
        font.pixelSize: Utils.mainText - 2
    }

    MouseArea {
        id: mouse3
        hoverEnabled: true
        anchors.fill: parent
        onClicked: {
            delegateRect.lv.currentIndex = delegateRect.index;
            delegateRect.lv.forceActiveFocus()
        }
    }
}
