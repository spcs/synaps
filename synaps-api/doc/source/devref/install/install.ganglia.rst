.. _install.ganglia:

Ganglia 설치하기
````````````````

본 문서에서는 기본적인 설치 방법만 가이드 한다. 보다 자세한 설치 및 설정관련
정보는 Ganglia 홈페이지를 참조한다.

서버(gmetad) 설치
-----------------

아래와 같이 Ganglia Server 를 설치한다. (gmetad 노드)

.. code-block:: bash

  apt-get install gmetad
  apt-get install ganglia-webfrontend
  cp /etc/ganglia-webfrontend/apache.conf /etc/apache2/sites-enabled/
  
Ganglia 서버 설정(/etc/ganglia/gmetad.conf)은 아래와 같다. 구성한 클러스터의 
이름을 등록 해주며, 클러스터의 main node를 등록

::

  data_source "Cluster Name1" 30 ###.###.###.###:8662
  data_source "Cluster Name2" 30 ###.###.###.###:8663
  
  gridname "Cluster GRID NAME"
  

Main Node(gmond) 설치 (전체 노드 중 하나)
-----------------------------------------

.. code-block:: bash

  apt-get install gmetad
  
Main Node 설정(/etc/ganglia/gmond.conf) 

data_source는 ganglia agent가 설치된 모든 노드를 등록해주며, trusted_hosts 
nagios 의 모든 노드를 등록해준다.

::

  data_source "Cluster Name" 30 ###.###.###.###:8663 ###.###.###.###:8663 ###.###.###.###:8663 ###.###.###.###:8663

  trusted_hosts nagios1 nagios2


Agent 설치 (전체 노드)
----------------------

.. code-block:: bash

  apt-get install ganglia-monitor
  
Ganglia Agent 설정은 아래와 같다. 클러스터 이름과 포트는 클러스터별로 다르게 
정해주며, Host는 Ganglia Main node로 지정.

::

  globals {
  daemonize = yes
  setuid = yes
  user = nobody
  debug_level = 0
  max_udp_msg_len = 1472
  mute = no
  deaf = no
  host_dmax = 0 /*secs */
  cleanup_threshold = 300 /*secs */
  gexec = no
  send_metadata_interval = 30
  }
  
  cluster {
  name = "Cluster name"
  owner = "unspecified"
  latlong = "unspecified"
  url = "unspecified"
  }

  /* Feel free to specify as many udp_send_channels as you like.  Gmond
  used to only support having a single channel */
  udp_send_channel {
  host = ###.###.###.###
  port = 8663
  ttl = 1
  }

  /* You can specify as many udp_recv_channels as you like as well. */
  udp_recv_channel {
  port = 8663
  }
  
  /* You can specify as many tcp_accept_channels as you like to share
  an xml description of the state of the cluster */
  tcp_accept_channel {
  port = 8663
  }
