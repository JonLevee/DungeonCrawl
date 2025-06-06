using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class ObjectProperty
{
    public string objectName;
    public List<KeyValue> properties = new();
}

[Serializable]
public class KeyValue
{
    public string key;
    public string value;
}

public class CustomFbxMetadata : MonoBehaviour
{
    public List<ObjectProperty> metadata = new();
}
