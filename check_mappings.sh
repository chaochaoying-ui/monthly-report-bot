#!/bin/bash
cd monthly_report_bot_link_pack
echo "检查用户ID映射情况"
echo "===================="
echo ""

ids="ou_07443a67428d8741eab5eac851b754b9
ou_0bbab538833c35081e8f5c3ef213e17e
ou_17b6bee82dd946d92a322cc7dea40eb7
ou_2f93cb9407ca5a281a92d1f5a72fdf7b
ou_33d81ce8839d93132e4417530f60c4a9
ou_3b14801caa065a0074c7d6db8603f288
ou_50c492f1d2b2ee2107c4e28ab4416732
ou_5199fde738bcaedd5fcf4555b0adf7a0
ou_66ef2e056d0425ac560717a8b80395c3
ou_9847326a1fea8db87079101775bd97a9
ou_b96c7cd4a604dc049569102d01c6c26d
ou_c9d7859417eb0344b310fcff095fa639
ou_d85dd7bb7625ab3e3f8b129e54934aea
ou_df1bfcd8e72f347c19e127154e7e618b
ou_f5338c49049621c36310e2215204d0be"

for id in $ids; do
    if grep -q "$id" monthly_report_bot_ws_v1.1.py; then
        name=$(grep "$id" monthly_report_bot_ws_v1.1.py | sed 's/.*: "//' | sed 's/".*//' | head -1)
        echo "✅ $id -> $name"
    else
        echo "❌ $id -> 未映射"
    fi
done
