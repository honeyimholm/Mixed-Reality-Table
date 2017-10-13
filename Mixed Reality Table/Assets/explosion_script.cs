using UnityEngine;
using System.Collections;

public class explosion_script : MonoBehaviour {

	// Use this for initialization
	void Start () {
        Invoke("Die", 1f);
	}
	
	// Update is called once per frame
	void Die () {
        Destroy(gameObject);
	}
}
