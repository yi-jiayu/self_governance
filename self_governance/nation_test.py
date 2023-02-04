import xml.etree.ElementTree as ET


class TestNation:
    def test_parse_issues(self):
        with open("issues.xml") as f:
            data = f.read()
        tree = ET.fromstring(data)
        root = tree.getroot()
