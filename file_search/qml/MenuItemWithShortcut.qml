// MenuItemWithShortcut.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

MenuItem {
    id: root

    property alias mainText: labelText.text
    property alias shortcutText: shortcutLabel.text
    property alias textColor: labelText.color
    property alias shortcutColor: shortcutLabel.color

    // Default text colors
    textColor: "black"
    shortcutColor: "gray"

    visible:mainText == "" ? false:true
    height:mainText == "" ? 0 : implicitHeight

    contentItem: RowLayout {
        spacing: 10
        Text {
            id: labelText
            Layout.fillWidth: true
            elide: Text.ElideRight
            font:root.font
        }
        Text {
            id: shortcutLabel
            font:root.font
        }
    }
}
