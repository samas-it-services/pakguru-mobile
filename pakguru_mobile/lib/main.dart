import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';

void main() {
  runApp(PakGuruMobile());
}

class PakGuruMobile extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PakGuru Mobile',
      theme: ThemeData(
        primarySwatch: Colors.red,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<dynamic> videos = [];
  bool isLoading = false;
  int currentPage = 0;
  final int videosPerPage = 5;
  TextEditingController searchController = TextEditingController();
  ScrollController scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    fetchVideos();
    scrollController.addListener(() {
      if (scrollController.position.pixels ==
          scrollController.position.maxScrollExtent) {
        fetchVideos();
      }
    });
  }

  Future<void> fetchVideos() async {
    if (isLoading) return;
    setState(() {
      isLoading = true;
    });

    // Simulating API call delay
    await Future.delayed(Duration(seconds: 1));

    // Use this for local JSON (db.json) backend
    final response = await http.get(Uri.parse('http://localhost:3000/videos'));

    // Use this for Firebase backend (uncomment and replace with your Firebase URL)
    // final response = await http.get(Uri.parse('https://your-firebase-url.com/videos'));

    if (response.statusCode == 200) {
      final newVideos = json.decode(response.body);
      setState(() {
        videos.addAll(
            newVideos.skip(currentPage * videosPerPage).take(videosPerPage));
        currentPage++;
        isLoading = false;
      });
    } else {
      setState(() {
        isLoading = false;
      });
      throw Exception('Failed to load videos');
    }
  }

  Widget buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: TextField(
        controller: searchController,
        decoration: InputDecoration(
          hintText: 'Search videos...',
          prefixIcon: Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(25.0),
          ),
        ),
        onSubmitted: (value) {
          // Implement search functionality here
          print('Searching for: $value');
        },
      ),
    );
  }

  Widget buildVideoPanel(dynamic video) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          YoutubePlayer(
            controller: YoutubePlayerController(
              initialVideoId: YoutubePlayer.convertUrlToId(video['video_url'])!,
              flags: YoutubePlayerFlags(autoPlay: false),
            ),
            showVideoProgressIndicator: true,
          ),
          Padding(
            padding: EdgeInsets.all(8.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  video['title'],
                  style: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 4.0),
                Text(
                  video['description'],
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                SizedBox(height: 8.0),
                Wrap(
                  spacing: 4.0,
                  children: buildTags(video['tags']),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> buildTags(List<dynamic> tags) {
    return tags
        .map((tag) => Chip(
              label: Text(tag),
              backgroundColor: Colors.grey[300],
            ))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Image.asset('assets/pakguru_logo.png', height: 40),
        centerTitle: true,
      ),
      body: Column(
        children: [
          buildSearchBar(),
          Expanded(
            child: ListView.builder(
              controller: scrollController,
              itemCount: videos.length + 1,
              itemBuilder: (context, index) {
                if (index < videos.length) {
                  return buildVideoPanel(videos[index]);
                } else if (index == videos.length && isLoading) {
                  return Center(child: CircularProgressIndicator());
                } else {
                  return SizedBox.shrink();
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}
