Three distinct jumps were printed and checked directly against the original replay. Event indices are zero-based. The initial DRAGON order assigns the ids, and the initial team field assigns A/B. The separate `raw-checks.json` retains the counter's event records. The original replay events below were printed independently of the counter.

### Our queen: game 980157, Stripes, meow A, id 1 (G=1, J=1)

```text
EDGE 560 2 3
EDGE 561 2 3
578 r18 turnStart id=1
579 r18 dragonAction id=1 action=move dirs=[2]
580 r18 dragonUpdate id=1 head=(11,11) tail=(10,10)
1128 r33 dragonAction id=4 action=move dirs=[2]
1129 r33 dragonDeath id=1 reason_code=3 (head-on)
```

The head immediately before event 580 was (10,10), independently recovered from preceding updates/splits. Width 24 gives an edge-index stride of 25. Edge 560 is the north edge of (10,11), and edge 561 is the north edge of (11,11); both have label 3. Moving south from (10,10) crosses edge 560 and lands at (11,11). The normal wrapped Manhattan displacement is 2, greater than one. Confirmed: one counted jump at r18.

At that event the enemy heads were id 0 at (14,1) and id 4 at (21,8). Landing distances are 3+2=5 and 10+3=13; nearest distance is 5, in 4–8. Own/enemy queen start distances are 10/12, so this is not other-side. The queen died during enemy id 4's move at r33: 33−18=15 rounds, within 30 but not within 10. Confirmed against death event 1129.

### Top-three queen: game 1006642, Default, Vibing++ B, id 1 (G=1, J=1)

```text
EDGE 1591 2 1
EDGE 1875 2 1
1773 r19 turnStart id=1
1774 r19 dragonAction id=1 action=move dirs=[2]
1775 r19 dragonUpdate id=1 head=(27,28) tail=(7,22)
32424 r162 dragonAction id=1 action=split
32425 r162 dragonDeath id=1 reason_code=4 (no action)
```

The previous head was (7,23). Width 32 gives stride 33. Edge 1591 is the north edge of (7,24); edge 1875 is the north edge of (27,28). Both have label 1. South crosses the first edge and lands at (27,28). Normal wrapped displacement is 12+5=17, greater than one. Confirmed: one counted jump at r19.

The independently recovered enemy heads were (24,11), (7,7), (19,7), (8,2), (10,29), (20,0), (21,29), (1,30). The closest was id 14 at (21,29): 6+1=7, in 4–8; the next closest was (1,30), at 8. Own/enemy start distances are 7/9, so this is not other-side. Death was at r162: 162−19=143, outside both windows.

### Death within 10: game 980565, Stripes, chaoliangUNSW B, id 0 (G=1, J=1)

```text
EDGE 53 2 6
EDGE 54 2 6
EDGE 78 1 -1
2858 r55 dragonAction id=0 action=move dirs=[0]
2859 r55 tileChange
2860 r55 dragonUpdate id=0 head=(3,0) tail=(5,0)
3348 r60 dragonAction id=0 action=move dirs=[1]
3349 r60 dragonDeath id=0 reason_code=0 (wall)
```

The previous head was (4,1). Edge 54 is the north edge of (4,1); edge 53 is the north edge of (3,1). Both have label 6. North crosses edge 54 and lands on the north side of edge 53, at (3,0). Normal displacement is 1+1=2. Confirmed: one counted jump at r55.

The only enemy head was id 3 at (15,7), distance 12+5=17; none was within 15, confirming “not seen.” Own queen start was (21,1), enemy queen start was (2,10): landing distances are 7 and 3, confirming other-side. At r60 the queen's head was (2,1); its east move hits edge 78, the west edge of (3,1), marked wall. Death code 0 confirms wall. 60−55=5 rounds, within both 10 and 30. This confirms the counted death window, without claiming that the jump caused the death.
