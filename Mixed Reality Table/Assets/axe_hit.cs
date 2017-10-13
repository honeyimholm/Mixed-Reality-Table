using UnityEngine;
using System.Collections;

public class axe_hit : MonoBehaviour {

    public GameObject explosion;
    void OnTriggerEnter2D(Collider2D other)
    {
        //can't destroy other axes
        if(other.gameObject.transform.name.ToString() != "axe")
        {
            Instantiate(explosion, other.transform.position, Quaternion.identity);
            Destroy(other.gameObject);

        }
        
    }
}
