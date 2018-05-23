#!/usr/bin/env perl
use Mojolicious::Lite;
use Data::Dumper;
use v5.20;
use experimental 'signatures';

get '/' => sub {
  my $self = shift;
  my $h = $self->req->headers->header('X-ClIENT-VERIFY');
  $self->render('text', "hello! did you verify? $h");
};

get '/login' => sub {
  my $h = $self->req->headers->header('X-ClIENT-VERIFY');
  my $self = shift;
  my $verify = $self->req->headers->header('X-SSL-ClIENT-S-DN');
  if ($VERIFY eq 'SUCCESS') {
    $self->render('text', "hello from the app! here is the client cert subject DN: $h");
  } else {
    $self->redirect_to('/');
  };
};

app->start;
