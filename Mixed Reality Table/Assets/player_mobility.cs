using UnityEngine;
using System.Collections;

public class player_mobility : MonoBehaviour {

    public float speed;
    private Vector3 debug;
    private Vector3 mouseOffset;
    public GameObject other;
    // Update is called once per frame
    void Start()
    {
        Cursor.visible = false;
    }
    void FixedUpdate()
    {
        //TODO: when within certain range of mouse, don't rotate
        var mousePosition = Camera.main.ScreenToWorldPoint(Input.mousePosition);
        //TODO: this doesn't prevent quick rotation
        if (Vector3.Distance(mousePosition, transform.position) > .1f)
        {
            Quaternion rot = Quaternion.LookRotation(transform.position - mousePosition, Vector3.forward);
            transform.rotation = rot;
            transform.eulerAngles = new Vector3(0, 0, transform.eulerAngles.z);
        }
        GetComponent<Rigidbody2D>().angularVelocity = 0;
        GetComponent<Rigidbody2D>().AddForce(gameObject.transform.up * speed);
        debug = gameObject.transform.up* speed;
        
        //print(debug.ToString());
        //print("speed: " + speed.ToString());
    }
}
